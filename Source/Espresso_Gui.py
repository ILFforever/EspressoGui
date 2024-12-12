import dearpygui.dearpygui as dpg
from pathlib import Path
import subprocess as sp
dpg.create_context()

cur_path = Path.cwd()
winw = 675
winh = 500

def close_window(sender, app_data, user_data):
    dpg.configure_item(user_data, show=False)

def change_extension(file_path, new_extension):
    path = Path(file_path)
    new_file_path = path.with_suffix('.' + new_extension)
    if new_file_path.exists():
        new_file_path.unlink()
        print(f"Old '{new_file_path}' exists and has been removed.")
    path.rename(new_file_path)
    print(f"File renamed to: {new_file_path}")
def populate_results(VarInputlist, VarOutputlist, Output1, Output2, Output3):
    dpg.set_value("input_vars_text", f"Input Variables ({len(VarInputlist)}) : {' ,'.join(VarInputlist)}  ||  ")
    dpg.set_value("output_vars_text", f"Output Variables ({len(VarOutputlist)}) : {' ,'.join(VarOutputlist)}")
    dpg.set_value("truth_table_output", Output1)
    dpg.set_value("sop_output", Output2.stdout)
    dpg.set_value("pos_output", Output3.stdout)
    dpg.configure_item("Results", show=True)
    dpg.configure_item("text_box", show=False)
    dpg.configure_item("missing", show=False)
    
    
def calc(sender, app_data, user_data):
    VarInput: str = dpg.get_value("InputVars")
    VarOutput: str = dpg.get_value("OutputVars")
    TTB: str = dpg.get_value("TTB")
    lines = TTB.splitlines() 
    while lines and not lines[-1].strip(): #remove trailing empty lines
        lines.pop()
    EspressoPath = Path(str(cur_path) +"/Espresso.exe") #does not return actual path for some reason (only works in .exe)
    if (VarInput == "") or (VarOutput == ""):
        dpg.configure_item("text_box", show=True)
        InPass = False
    else: 
        InPass = True
    if not EspressoPath.exists():
        dpg.configure_item("missing", show=True)
        EPass = False
    else:
        EPass = True
    if InPass and EPass:
        dpg.configure_item("text_box", show=False)
        VarInputlist = VarInput.split()
        VarOutputlist = VarOutput.split()
        file_path = str(cur_path) + "/temp.txt"
        result_path = str(cur_path) + "/Outtemp.pla"
        read_path = str(cur_path) + "/Outtemp.txt"
        with open(file_path, 'w') as file:
            file.write(".i " + str(len(VarInputlist))+"\n")
            file.write(".o " + str(len(VarOutputlist))+"\n")
            file.write(".ilb " + str(' '.join(VarInputlist))+"\n")
            file.write(".ob " + str(' '.join(VarOutputlist))+"\n")
            file.write(".p " + str(len(lines))+"\n")
            file.write(TTB + "\n")
            file.write(".e")
        change_extension(file_path, "pla")

        for i in range(3):
            if i == 0:
                command  = "espresso temp.pla > Outtemp.pla"
                result = sp.run(command,shell=True,capture_output=True,text=True)
                print(result)
                change_extension(result_path, "txt")
                with open(read_path, 'r') as file:
                    Output1 = file.read()
            elif i == 1:
                command  = "espresso -o eqntott temp.pla"
                Output2 = sp.run(command,shell=True,capture_output=True,text=True)
            elif i == 2:
                command  = "espresso -epos -o eqntott temp.pla"
                Output3 =  sp.run(command,shell=True,capture_output=True,text=True)
        populate_results(VarInputlist, VarOutputlist, Output1, Output2, Output3)
    
def create_results_window():        
    with dpg.window(label="Results", width= winw, height= winh, tag="Results", no_move=True, no_collapse=True):
        with dpg.group(horizontal=True):
            dpg.add_text("Input Variables: ", tag="input_vars_text")
            dpg.add_text("Output Variables: ", tag="output_vars_text")
        dpg.add_input_text(multiline=True, height=300, width=450, label="Truth Table", tag="truth_table_output")
        dpg.add_input_text(multiline=False, label="Sum of Products", tag="sop_output")
        dpg.add_input_text(multiline=False, label="Product of Sums", tag="pos_output")
        dpg.configure_item("text_box", show=False)
        dpg.configure_item("Results", show=False)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Back to Home",callback=close_window,user_data="Results")

with dpg.window(label="Home", width= winw, height= winh, tag="Home", no_move=True, no_collapse=True):
    with dpg.group(horizontal=True):
        dpg.add_input_text(hint= "List of input Names seperated by a space",width=320, tag="InputVars")
        VarOutputlist = dpg.add_input_text(hint= "List of output Names seperated by a space",width=320,tag="OutputVars")
    dpg.add_spacer(height=2)
    dpg.add_text("Input Truth Table")
    dpg.add_input_text(multiline=True, height=300, width=500,tag= "TTB")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Calculate", callback=calc)
        dpg.add_text("Input Error!", tag="text_box", show=False,color=[255, 0, 0, 255])
        dpg.add_text("Espresso.exe Missing!", tag="missing", show=False,color=[255, 0, 0, 255])
    with dpg.group(horizontal=True):
        dpg.add_spacer(height=100,width=520)
        dpg.add_text("Ver 1.2 by Hammy",color=[169, 169, 169, 100])
        
create_results_window()
dpg.create_viewport(title='Espresso Gui', width=winw, height=winh,resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()