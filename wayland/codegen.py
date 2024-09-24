import argparse
import io
import sys
from pathlib import Path

from .base import ArgFd, ArgNewId, ArgObject, ArgUInt, Protocol, WEvent, WRequest


def generate_client(
    proto: Protocol,
    reliative: bool,
    deps: set[str],
) -> str:
    """Generate client proxies from protocol"""
    interfaces = proto.interfaces
    module = io.StringIO()
    if reliative:
        wayland_base = "..base"
    else:
        wayland_base = "wayland.base"
    print(
        "# Auto generated do not edit manually\n"
        "# fmt: off\n"
        "# pyright: reportPrivateUsage=false\n"
        "from __future__ import annotations\n"
        "from enum import Enum, Flag\n"
        "from typing import Any, ClassVar\n"
        "from collections.abc import Callable\n"
        f"from {wayland_base} import *",
        file=module,
    )
    for dep in deps:
        print(f"from .{dep} import *", file=module)
    print(file=module)

    print("__all__ = [", file=module)
    for iface_name in interfaces:
        print(f'    "{_camle_case(iface_name)}",'.format(iface_name), file=module)
    print("]\n", file=module)

    for iface_name, interface in interfaces.items():
        # define class
        class_name = _camle_case(iface_name)
        print(f"class {class_name}(Proxy):", file=module)
        if interface.summary is not None:
            print(f'    """{interface.summary}"""', file=module)

        # define interface
        print(f"    interface: ClassVar[Interface] = Interface(", file=module)
        print(f'        name="{iface_name}",', file=module)
        print(f"        requests=[", file=module)
        for request in interface.requests:
            print(
                f'            WRequest("{request.name}", {request.args}),',
                file=module,
            )
        print(f"        ],", file=module)
        print(f"        events=[", file=module)
        for event in interface.events:
            print(f'            WEvent("{event.name}", {event.args}),', file=module)
        print(f"        ],", file=module)
        print("        enums=[", file=module)
        for enum in interface.enums:
            print("            WEnum(", file=module)
            print(f'                name="{enum.name}",', file=module)
            print(f"                values={{", file=module)
            for var_name, value in enum.values.items():
                print(f'                    "{var_name}": {value},', file=module)
            print("                },", file=module)
            if enum.flag:
                print(f"                flag=True,", file=module)
            print("            ),", file=module)
        print("        ],", file=module)
        print(f"    )\n", file=module)

        # define init
        print(
            f"    def __init__(self, id: Id, connection: Connection) -> None:\n"
            f"        super().__init__(id, connection, self.interface)\n",
            file=module,
        )

        # define requests
        destructor: str | None = None
        for opcode, request in enumerate(interface.requests):
            if request.destructor and not request.args:
                destructor = request.name
            _generate_request(module, opcode, request)

        # destroy scope
        if destructor:
            print(
                f"    def __enter__(self) -> {class_name}:\n"
                f"        return self\n"
                "\n"
                f"    def __exit__(self, *_: Any) -> None:\n"
                f"        self.{destructor}()\n",
                file=module,
            )

        # define events
        for opcode, event in enumerate(interface.events):
            _generate_events(module, opcode, event)

        # define enums
        enums: dict[str, str] = {}
        for enum in interface.enums:
            enum_name = _camle_case(enum.name)
            enums[enum.name] = enum_name
            enum_type = "Flag" if enum.flag else "Enum"
            print(f"    class {enum_name}({enum_type}):", file=module)
            for var_name, value in enum.values.items():
                # prefix digit only enums with "U"
                prefix = "U" if var_name.isdigit() else ""
                print(f"        {prefix}{var_name.upper()} = {value}", file=module)
            print(file=module)
        if enums:
            module.write(
                f"def _unpack_enum_{iface_name}(name: str, value: int) -> Any:\n"
            )
            for enum_name, enum_type in enums.items():
                print(
                    f'    if name == "{enum_name}":\n'
                    f"        return {class_name}.{enum_type}(value)",
                    file=module,
                )
            module.write("    return None\n")
            module.write(
                f"{class_name}.interface.unpack_enum = _unpack_enum_{iface_name}\n\n"
            )

        module.write(f'PROXIES["{iface_name}"] = {class_name}\n\n')

    module.write("# fmt: on")
    return module.getvalue()


def _generate_request(
    module: io.StringIO,
    opcode: int,
    request: WRequest,
) -> None:
    results_desc: list[ArgNewId] = []
    args_types: list[str] = []
    for arg_desc in request.args:
        if isinstance(arg_desc, ArgObject):
            arg_type: str
            if arg_desc.interface is None:
                arg_type = "Proxy"
            else:
                arg_type = _camle_case(arg_desc.interface)
            if arg_desc.optional:
                arg_type = f"{arg_type} | None"
            args_types.append(f"{arg_desc.name}: {arg_type}")
        elif isinstance(arg_desc, ArgNewId):
            if arg_desc.interface is None:
                args_types.append(f"{arg_desc.name}: Proxy")
            results_desc.append(arg_desc)
        elif isinstance(arg_desc, ArgFd):
            args_types.append(f"{arg_desc.name}: Fd")
        elif isinstance(arg_desc, ArgUInt):
            if arg_desc.enum is None:
                args_types.append(f"{arg_desc.name}: {arg_desc.type_name}")
            else:
                args_types.append(f"{arg_desc.name}: {_camle_case(arg_desc.enum)}")
        else:
            args_types.append(f"{arg_desc.name}: {arg_desc.type_name}")

    # method type
    args = ""
    if args_types:
        args = ", " + ", ".join(args_types)
    if not results_desc:
        result_type = "None"
    elif len(results_desc) == 1:
        desc = results_desc[0]
        result_type = f"{_camle_case(desc.interface)}" if desc.interface else "None"
    else:
        results = (
            f"{_camle_case(desc.interface)}" for desc in results_desc if desc.interface
        )
        result_type = "Tuple[{}]".format(", ".join(results))
    print(f"    def {request.name}(self{args}) -> {result_type}:", file=module)
    if request.summary:
        print(f'        """{request.summary}"""', file=module)

    # proxies
    result_vals: list[str] = []
    for result_desc in results_desc:
        name = result_desc.name
        if result_desc.interface is None:
            print(
                f"        _proxy_iface = {name}._interface.name\n"
                f"        if _proxy_iface != {name}_interface:\n"
                f'            raise TypeError("[{{}}({name})] expected {{}} (got {{}})"\n'
                f"                            .format(self, {name}_interface, _proxy_iface))",
                file=module,
            )
            continue
        print(
            f"        {name} = self._connection.create_proxy({_camle_case(result_desc.interface)})",
            file=module,
        )
        result_vals.append(result_desc.name)

    # submit
    values = "tuple()"
    if request.args:
        values = "({},)".format(", ".join(arg.name for arg in request.args))
    print(
        f"        self._call(OpCode({opcode}), {values})\n"
        f'        return {",".join(result_vals) if result_vals else None}\n',
        file=module,
    )


def _generate_events(
    module: io.StringIO,
    opcode: int,
    event: WEvent,
) -> None:
    args_types: list[str] = []
    for arg_desc in event.args:
        if isinstance(arg_desc, (ArgObject, ArgNewId)):
            arg_type: str
            if arg_desc.interface is None:
                arg_type = arg_desc.type_name
            else:
                arg_type = _camle_case(arg_desc.interface)
            if isinstance(arg_desc, ArgObject) and arg_desc.optional:
                arg_type = f"{arg_type} | None"
            args_types.append(arg_type)
        elif isinstance(arg_desc, ArgUInt) and arg_desc.enum:
            args_types.append(_camle_case(arg_desc.enum))
        else:
            args_types.append(arg_desc.type_name)
    handler_sig = "Callable[[{}], bool]".format(", ".join(args_types))
    print(
        f"    def on_{event.name}(self, handler: {handler_sig}) -> {handler_sig} | None:",
        file=module,
    )
    if event.summary:
        print(f'        """{event.summary}"""', file=module)
    print(
        f"        _opcode = OpCode({opcode})\n"
        f"        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler\n"
        f"        return old_handler\n",
        file=module,
    )


def _camle_case(name: str) -> str:
    """Convert name to CamelCase"""
    upper = True
    chars: list[str] = []
    for char in name:
        if char == "_":
            upper = True
            continue
        if upper:
            chars.append(char.upper())
            upper = False
        else:
            chars.append(char)
        if char == ".":
            upper = True
    return "".join(chars)


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument("--proto", required=False, help="input protocol xml file")
    opts = args.parse_args()

    if opts.proto:
        protocol = Protocol.load(opts.proto)
        print(generate_client(protocol, reliative=False, deps=set()))
        return

    protocols: list[Protocol] = []
    path = Path("protocol")
    for proto_file in path.iterdir():
        if proto_file.suffix != ".xml":
            continue
        protocols.append(Protocol.load(str(proto_file)))

    deps: dict[str, set[str]] = {proto.name: set() for proto in protocols}
    for protocol in protocols:
        for extern in protocol.extern:
            for dep in protocols:
                if extern in dep.interfaces:
                    deps[protocol.name].add(dep.name)

    target = Path(__file__).parent / "protocol"
    for protocol in protocols:
        print(protocol.name, file=sys.stderr)
        module = generate_client(protocol, reliative=True, deps=deps[protocol.name])
        module_file = target / f"{protocol.name}.py"
        module_file.write_text(module)


if __name__ == "__main__":
    main()
