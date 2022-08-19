
from string import Template
from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Prompt
from module_strings import register_template, esp_get_template, esp_set_template, regmap_template
import sys

panel_string = """Welcome to ESP codegenerator!
    a) Generate Register map
    b) Generate Getters/Setters
    c) Generate Getters/Setters from Register map

    q) Quit
"""

regmap_string = """ Register Map Creator
    a) Add new register
    b) Remove last register
    c) Review registers so far
    d) Save Register map
    e) Return

    Current Registers: $x

    q) Quit
"""

reg_string = """ Add Register
    Register Name: $x
    Register Address: $a
    Register Default $d
    Register Contents: 
        $c
"""


POSIX_CLS = "\033c"

last_register_map = []

def register_to_dict(regname, address, default, contents=[]):
    return {
        "regname": regname,
        "address": address,
        "contents": contents,
        "default": default
    }


def refresh_screen(output):
    print(POSIX_CLS)
    rprint(output)

def create_register():

    contents_master = ""
    contents = []
    regstring = Template(reg_string)
    out = regstring.substitute({"x": "", "a": "", "c": "", "d": ""})    
    p = Panel(out)
    refresh_screen(p)

    regname = Prompt.ask("Enter Register name: ")
    regname.replace(" ", "_")
    out = regstring.substitute({"x": regname, "a": "", "c": "", "d": ""})
    p = Panel(out)
    refresh_screen(p)

    address = Prompt.ask("Enter Register Address: ")
    _san_addr = int(address, 16) if address.startswith("0x") else int(address)
    address = hex(_san_addr)
    out = regstring.substitute({"x": regname, "a": address, "c": "", "d": ""})
    p = Panel(out)
    refresh_screen(p)

    default = Prompt.ask("Enter default value: ")
    _san_def = int(default, 16) if default.startswith("0x") else int(default)
    _def = hex(_san_def)
    out = regstring.substitute({"x": regname, "a": address, "c": "", "d": _def})
    p = Panel(out)
    refresh_screen(p)

    bits = 0
    l = ""
    while l != "z" and bits < 8:
        rprint(Panel("Enter Register contents (MSB First) - press 'z' to finish"))
        l = Prompt.ask("Enter field name: ")
        l.replace(" ", "_")
        valid = False

        while not valid:
            b = Prompt.ask("Enter bit size: ")
            b.replace(" ", "")
            try:
                b = int(b)
                if b == 0:
                    raise ValueError
                bits += b
                if bits > 8:
                    ValueError("Error! More than 8 bits used")
                valid = True
            except ValueError:
                rprint("Invalid value! (1-8)")
        contents_master += f"uint8_t {l}\t\t:\t{b};\n"
        contents.append({'name': l, 'bits': b})
        out = regstring.substitute({"x": regname, "a": address, "c": contents_master, "d": _def})
        p = Panel(out)
        refresh_screen(p)

    out = regstring.substitute({"x": regname, "a": address, "c": contents_master, "d": _def})
    p = Panel(out)
    refresh_screen(p)

    _r = register_template.substitute({"contents": contents_master, "reg_name": regname})

    rprint("Done! Press any key to return")
    h = Prompt.ask("")
    return _r, register_to_dict(regname, address, _def, contents)


def create_regmap(regname):
    registers = []
    done = False
    while not done:
        print(POSIX_CLS)
        menu = Template(regmap_string)
        output = menu.substitute({'x': len(registers)})
        rprint(Panel(output))

        choice = Prompt.ask(">>>", choices=["a", "b", "c", "d", "e", "q"])

        if choice == "a":
            r = create_register()
            registers.append(r)
            last_register_map.append(r[1])
        elif choice == "b" and len(registers) > 0:
            registers.pop()
        elif choice == "c":
            print(POSIX_CLS)
            panel_string = ""
            for x, reg in enumerate(registers):
                panel_string += f"{x}\t{reg}"
            refresh_screen(Panel(panel_string))
        elif choice == "d":
            content_string = ""
            last = []
            for r in registers:
                content_string += r[0]
                content_string += "\n"
                last.append(r[1])
            out = regmap_template.substitute({"contents": content_string, "regmap_name": regname})
            filepath = Prompt.ask("Enter Output file: ")
            with open(f"./{filepath}", "w") as f:
                f.write(out)
            rprint("Save succesful")
        elif choice == "e":
            done = True
        else:
            print("Bye!")
            sys.exit(0)


def create_function():
    pass

def create_functions():
    pass

def create_functions_from_reg():
    funcs = []
    params = []
    
    if len(last_register_map) == 0:
        rprint("No registers saved yet! Come back soon and we'll implement building from saved files")
        sys.exit(0)
    
    drivername = Prompt.ask("Enter driver short name: ")
    drivername.replace(" ", "_")

    handlename = Prompt.ask("Please enter the handle name")
    handlename.replace(" ", "_")

    for reg in last_register_map:
        cnt = reg["contents"]
        s = 0
        for c in cnt:
            details = {'name': c['name'], 'width': c['bits'], 'shift': s}
            s += c['bits']
            params.append(details)

    for x in params:
        get = esp_get_template.substitute({
            "drivername": drivername,
            "handlename": handlename,
            "param": x['name'],
            "vartype": ("uint8_t" if x['width'] > 1 else "bool"),
        })

        set = esp_set_template.substitute({
            "drivername": drivername,
            "handlename": handlename,
            "param": x['name'],
            "vartype": ("uint8_t" if x['width'] > 1 else "bool"),
            "limit": (2**x["width"])-1,
            "shift": x['shift']
            })

        funcs.append(get)
        funcs.append(set)

    path = Prompt.ask("Enter a Filename: ")
    path.replace(" ", "_")

    with open(path, "w") as f:
        for n in funcs:
            rprint(f"Adding {n} to file")
            f.write(n)
            f.write("\n")

    rprint("Done!")

    return


def main():

    while True:
        rprint(Panel(panel_string, title="ESP CODEGEN"))

        choice = Prompt.ask(">>>", choices=["a", "b", "c", "q"])

        if choice == "a":
            regname = Prompt.ask("Enter Regmap name: ")
            regname.replace(" ", "_")
            create_regmap(regname)
        elif choice == "b":
            create_functions()
        elif choice == "c":
            create_functions_from_reg()
        else:
            rprint("Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()