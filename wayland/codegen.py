import io
import argparse
from typing import List
from .client import Arg, ArgFd, ArgNewId, ArgObject, load_protocol


def generate_client(path: str) -> str:
    """Generate client proxies from protocol"""
    interfaces = load_protocol(path)
    module = io.StringIO()
    print(
        "# Auto generated do not edit manualy\n"
        "# fmt: off\n"
        "# pyright: reportPrivateUsage=false\n"
        "from typing import ClassVar\n"
        "from wayland.client import (\n"
        "    ArgUInt,\n"
        "    ArgInt,\n"
        "    ArgFixed,\n"
        "    ArgStr,\n"
        "    ArgArray,\n"
        "    ArgNewId,\n"
        "    ArgObject,\n"
        "    ArgFd,\n"
        "    Connection,\n"
        "    Fd,\n"
        "    Id,\n"
        "    Interface,\n"
        "    Message,\n"
        "    OpCode,\n"
        "    Proxy,\n"
        ")",
        file=module,
    )
    print("\n", file=module)
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
        print(f"    )\n", file=module)

        # define init
        print(
            f"    def __init__(self, id: Id, connection: Connection) -> None:\n"
            f"        super().__init__(id, self.interface, connection)\n",
            file=module,
        )

        # define requests
        for opcode, (request, args_desc) in enumerate(interface.requests):
            _generate_request(module, opcode, request, args_desc)

        # define events
        for opcode, (event, args_desc) in enumerate(interface.events):
            _generate_event(module, opcode, event, args_desc)

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


def _generate_event(
    module: io.StringIO,
    opcode: int,
    event: str,
    args_desc: List[Arg],
) -> None:
    pass


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("protocol_xml", help="input protocol xml file")
    opts = args.parse_args()
    print(generate_client(opts.protocol_xml))
