import io
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set
from .client import Arg, ArgFd, ArgNewId, ArgObject, ArgUInt, Protocol


def generate_client(
    proto: Protocol,
    reliative: bool,
    deps: Set[str],
) -> str:
    """Generate client proxies from protocol"""
    interfaces = proto.interfaces
    module = io.StringIO()
    if reliative:
        wayland_client = "..client"
    else:
        wayland_client = "wayland.client"
    print(
        "# Auto generated do not edit manually\n"
        "# fmt: off\n"
        "# pyright: reportPrivateUsage=false\n"
        "from enum import Enum\n"
        "from typing import Callable, ClassVar, Optional\n"
        f"from {wayland_client} import *",
        file=module,
    )
    for dep in deps:
        print(f"from .{dep} import *", file=module)
    print(file=module)

    print("__all__ = [", file=module)
    for iface_name in interfaces:
        print(f'    "{iface_name}",'.format(iface_name), file=module)
    print("]\n", file=module)

    for iface_name, interface in interfaces.items():
        # define class
        print(f"class {iface_name}(Proxy):", file=module)

        # define interface
        print(f"    interface: ClassVar[Interface] = Interface(", file=module)
        print(f'        name="{iface_name}",', file=module)
        print(f"        requests=[", file=module)
        for request, args_desc in interface.requests:
            print(f'            ("{request}", {args_desc}),', file=module)
        print(f"        ],", file=module)
        print(f"        events=[", file=module)
        for event, args_desc in interface.events:
            print(f'            ("{event}", {args_desc}),', file=module)
        print(f"        ],", file=module)
        print("        enums={", file=module)
        for enum_name, enum in interface.enums.items():
            print('            "{}": {{'.format(enum_name), file=module)
            for var_name, value in enum.items():
                print('                "{}": {},'.format(var_name, value), file=module)
            print("            },", file=module)
        print("        },", file=module)
        print(f"    )\n", file=module)

        # define init
        print(
            f"    def __init__(self, id: Id, connection: Connection) -> None:\n"
            f"        super().__init__(id, connection, self.interface)\n",
            file=module,
        )

        # define requests
        for opcode, (request, args_desc) in enumerate(interface.requests):
            _generate_request(module, opcode, request, args_desc)

        # define events
        for opcode, (event, args_desc) in enumerate(interface.events):
            _generate_events(module, opcode, event, args_desc)

        # define enums
        for enum_name, enum in interface.enums.items():
            print(f"    class enum_{enum_name}(Enum):", file=module)
            for var_name, value in enum.items():
                prefix = "u" if var_name.isdigit() else ""
                print(f"        {prefix}{var_name} = {value}", file=module)
            print(file=module)

    module.write("# fmt: on")
    return module.getvalue()


def _generate_request(
    module: io.StringIO,
    opcode: int,
    request: str,
    args_desc: List[Arg],
) -> None:
    results_desc: List[ArgNewId] = []
    args_types: List[str] = []
    for arg_desc in args_desc:
        if isinstance(arg_desc, ArgObject):
            if arg_desc.interface is None:
                args_types.append(f"{arg_desc.name}: Proxy")
            else:
                args_types.append(f'{arg_desc.name}: "{arg_desc.interface}"')
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
                chunks = arg_desc.enum.split(".")
                chunks[-1] = f"enum_{chunks[-1]}"
                enum_name = ".".join(chunks)
                args_types.append(f'{arg_desc.name}: "{enum_name}"')
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
        result_type = f'"{desc.interface}"' if desc.interface else "None"
    else:
        results = (f'"{desc.interface}"' for desc in results_desc if desc.interface)
        result_type = "Tuple[{}]".format(", ".join(results))
    print(
        f"    def {request}(self{args}) -> {result_type}:\n"
        f"        _opcode = OpCode({opcode})",
        file=module,
    )

    # proxies
    result_vals: List[str] = []
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
            f"        {name} = self._connection.create_proxy_typed({result_desc.interface})",
            file=module,
        )
        result_vals.append(result_desc.name)

    # submit
    values = "tuple()"
    if args_desc:
        values = "({},)".format(", ".join(arg_desc.name for arg_desc in args_desc))
    print(
        f"        _data, _fds = self._interface.pack(_opcode, {values})\n"
        f"        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))\n"
        f'        return {",".join(result_vals) if result_vals else None}\n',
        file=module,
    )


def _generate_events(
    module: io.StringIO,
    opcode: int,
    event: str,
    args_desc: List[Arg],
) -> None:
    args_types: List[str] = []
    for arg_desc in args_desc:
        if isinstance(arg_desc, (ArgObject, ArgNewId)):
            if arg_desc.interface is None:
                args_types.append(arg_desc.type_name)
            else:
                args_types.append(f'"{arg_desc.interface}"')
        else:
            args_types.append(arg_desc.type_name)
    handler_sig = "Callable[[{}], bool]".format(", ".join(args_types))
    print(
        f"    def on_{event}(self, handler: {handler_sig}) -> Optional[{handler_sig}]:\n"
        f"        _opcode = OpCode({opcode})\n"
        f"        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler\n"
        f"        return old_handler\n",
        file=module,
    )


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument("--protocol_xml", required=False, help="input protocol xml file")
    opts = args.parse_args()

    if opts.protocol_xml:
        protocol = Protocol.load(opts.protocol_xml)
        print(generate_client(protocol, reliative=False, deps=set()))
        return

    protocols: List[Protocol] = []
    path = Path("protocol")
    for proto_file in path.iterdir():
        if proto_file.suffix != ".xml":
            continue
        protocols.append(Protocol.load(str(proto_file)))

    deps: Dict[str, Set[str]] = {proto.name: set() for proto in protocols}
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
