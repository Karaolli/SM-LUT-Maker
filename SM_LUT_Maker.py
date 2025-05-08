manual = 0

operation_names = ["Addition", "Subtraction", "Multiplication", "Comparison", "(a * b) >> 4", "(a * b) & 15", "Sine", "1/A"]

def main(aBits, bBits, maxValueA, maxValueB, operation, zInverted_bool, custom_input, external_pla_bool, minimization_type, exact, fast, single_output, single_output_both, output_phase_optimization_all, strong, Quality, Cubes, espresso_args, width, length, length_fill, use_custom_path, blueprint_path, output_queue):
    if not manual:
        sys.stdout = QueueWriter(output_queue)
    else:
        aBits = 0
        bBits = 0
        maxValueA = 0
        maxValueB = 0
        operation = 0
        zInverted_bool = 0
        custom_input = 0
        external_pla_bool = 0
        minimization_type = 0  # 0 - SOP, 1 - POS, 2 - ESOP, 3 - don't minimize
        # Espresso arguments
        exact = 0
        fast = 0
        single_output = 0
        single_output_both = 0
        output_phase_optimization_all = 0
        strong = 0
        espresso_args = []
        # Exorcism options
        Quality = 0
        Cubes = 20000

        width = 1
        length = 1   #  height if length fill is 1
        length_fill = 0
        use_custom_path = 0   #   will save to root folder if 0   
        blueprint_path = "C:/Users"    #   paths should use forward slashes
    
    x = custom_input
    
    def operations(operation):   # to mark the entire output as don't care use   return "skip"
        if operation == 0:
            z = a + b
        elif operation == 1:
            z = a - b
            if z < 0:
                z += powZbits
        elif operation == 2:
            z = a * b
        elif operation == 3:
            z = (a >= b)
        elif operation == 4:
            c = (a * b) >> x
            z = dont_care(operation, c)
        elif operation == 5:
            z = (a * b) & ((1 << x) - 1)
        elif operation == 6:
            c = math.sin(2*math.pi * a/(1 << aBits))
            z = float_to_bin(c, x)
        elif operation == 7:
            if a != 0:
                z = float_to_bin(16/a, x)
            else: z = 0

        return z

    def operation_lengths(operation):   #     define the length of the output here.  if you want a specific amount of bits do  maxValueZ = (1 << your_number) - 1
        if operation == 0:
            maxValueZ = maxValueA + maxValueB
        elif operation == 1:
            maxValueZ = maxValueA
        elif operation == 2:
            maxValueZ = maxValueA * maxValueB
        elif operation == 3:
            maxValueZ = 1
        if operation == 4:
            maxValueZ = (maxValueA * maxValueB) >> 4
        elif operation == 5:
            maxValueZ = 15
        elif operation == 6:
            maxValueZ = (4 << x) - 1
        elif operation == 7:
            maxValueZ = (16 << x) - 1

        return maxValueZ

    def dont_care(operation, z):
        zbin = format(z, f'0{zBits}b')
        if operation == 4:
            for i in range(0, zBits // 2):
                truth.write('-')
            for i in range(zBits // 2, zBits):
                truth.write(zbin[i])
        return "customskip"
    
    def float_to_bin(number, precision: int):
        v = int(round(number * (1 << precision)))
        if v < 0:
            v += powZbits
        return v

    input_splits = [aBits]

    mask_fix = 0
    if not maxValueA:
        maxValueA = (1 << aBits) - 1
    if not maxValueB:
        maxValueB = (1 << bBits) - 1

    maxValueZ = operation_lengths(operation)
    zBits = len(bin(maxValueZ)) - 2

    output_splits = [zBits]
    inputs = aBits + bBits
    outputs = zBits + zBits * zInverted_bool
    powIbits = 1 << inputs
    powZbits = 1 << zBits
    def dont_care_line():
        for i in range(0, outputs):
            truth.write('-')
        truth.write('\n')
    if not external_pla_bool:
        print("Generating truth table...")
        with open("truth_generated.pla", "w") as truth:
            truth.write(f".i {inputs}\n")
            truth.write(f".o {outputs}\n")
            truth.write(f".p {powIbits}\n")
            for inputInt in range(0, powIbits):
                inputBin = format(inputInt, f'0{inputs}b')
                for i in range(0, inputs):
                    truth.write(inputBin[i])
                truth.write(' ')
                a = inputInt >> bBits
                b = inputInt - (a << bBits)
                if a > maxValueA or b > maxValueB:
                    dont_care_line()
                    continue
                z = operations(operation)
                if z == "skip":
                    dont_care_line()
                    continue
                elif z == "customskip":
                    truth.write('\n')
                    continue
                
                zbin = format(z, f'0{zBits}b')
                if zInverted_bool:
                    for i in range(len(zbin) - zBits, len(zbin)):
                        if zbin[i] == '1': truth.write('0')
                        else: truth.write('1')
                for i in range(0, zBits):
                    truth.write(zbin[i])
                truth.write('\n')
            truth.write(".e")
        print("Truth table generated")


    if minimization_type < 3:
        print("Minimizing...")
        global minimizer
        if minimization_type < 2:
            if minimization_type == 1: espresso_args.append("-epos")
            if exact: espresso_args.append("-Dexact")
            if fast: espresso_args.append("-efast")
            if single_output: espresso_args.append("-Dso")
            if single_output_both: espresso_args.append("-Dso_both")
            if output_phase_optimization_all: espresso_args.append("-Dopoall")
            if strong: espresso_args.append("-estrong")
            if external_pla_bool:
                espresso_args.append("../truth.pla")
            else:
                espresso_args.append("truth_generated.pla")
            print("Sending command:", ["espresso", *espresso_args])
            minimizer = subprocess.run(
                ["espresso", *espresso_args],
                capture_output=True,
                text = True
            )
            if minimizer.stderr:
                print("Errors: ", minimizer.stderr, end="")
                return
            with open("minimized.pla", "w") as minimized:
                minimized.write(minimizer.stdout)
            print("Minimized with Espresso")
        elif minimization_type == 2:
            minimizer = subprocess.Popen(
            ["abc"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            if external_pla_bool:
                truth_filename = "../truth.pla"
            else:
                truth_filename = "truth_generated.pla"
            stdout, stderr = minimizer.communicate(
            #"read_pla " + truth_filename + "; collapse; write_pla collapsed.pla; &exorcism -V 0 -Q " + str(Quality) + " -C " + str(Cubes) + " collapsed.pla minimized.pla"
            "&exorcism -V 0 -Q " + str(Quality) + " -C " + str(Cubes) + " " + truth_filename + " minimized.pla"
            )
            #print("Standard output: ", stdout)
            if not stdout.endswith("> "):
                print("Error: ", end='')
                if stdout.endswith(" cubes. Quitting...\nSomething went wrong when minimizing the cover\n"):
                    print("The size of the starting cover is more than", Cubes, "cubes. Quitting...\nTry increasing the maximum amount of cubes")
                    return
                elif stdout.endswith(" Unexpected memory allocation problem. Quitting...\nSomething went wrong when minimizing the cover\n"):
                    print("Unexpected memory allocation problem. Quitting...\nThe function is too big")
                    return
                else:
                    print("Unknown error")
                    print("Standard output: ", stdout)
                    return
            if stderr:
                print("Errors: ", stderr)
                return
            print("Minimized with Exorcism")


    blueprint = {"bodies":[{"childs":[]}],"dependencies":[{"contentId":"0d079c85-2b7a-4424-8d1b-5a9da6a4d59e","name":"Logic Gate Visibility Fix","shapeIds":["9f0f56e8-2c31-4d83-996c-d00a9b296c3f"],"steamFileId":3340095265}],"version":4}

    gate = {"color":"","controller":{"active":False,"controllers":[],"id":0,"joints":None,"mode":0},"pos":{"x":0,"y":0,"z":0},"shapeId":"9f0f56e8-2c31-4d83-996c-d00a9b296c3f","xaxis":-2,"zaxis":-1}
    switch = {"color":"DF7F01","controller":{"active":False,"controllers":[{"id":2}],"id":0,"joints":None},"pos":{"x":-3,"y":0,"z":2},"shapeId":"7cf717d7-d167-4f2d-a6e7-6b2c70aa3986","xaxis":1,"zaxis":-2}

    if minimization_type < 3:
        minimized_filename = "minimized.pla"
    elif external_pla_bool:
        minimized_filename = "../truth.pla"
    else:
        minimized_filename = "truth_generated.pla"
    with open(minimized_filename, "r") as pla:
        print("Building", end='')
        if length_fill:
            first_coordinate = "y"
        else:
            first_coordinate = "x"
        for linestr in pla:
            if linestr[0] == '#':
                continue
            line = linestr.split()
            if line[0] == ".i":       #          ________inputs
                inputs = int(line[1])
                inputs_stats = []
                gate["pos"]["x"] = -1
                blank = ""
                for i in range(0, inputs):
                    inputs_stats.append(0)
                    inputs_stats.append(0)
                    if i in input_splits:
                        gate["pos"]["x"] -= 2
                        gate["pos"]["y"] = 0
                        switch["pos"]["x"] -= 2
                        switch["pos"]["y"] = 0
                    gate["color"] = "0A3EE2"
                    gate["controller"]["mode"] = 1
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                    gate["controller"]["id"] += 1
                    gate["pos"]["x"] -= 1
                    gate["color"] = "0F2E91"
                    gate["controller"]["mode"] = 4
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                    gate["controller"]["id"] += 1
                    gate["pos"]["z"] += 1
                    gate["color"] = "0A3EE2"
                    gate["controller"]["mode"] = 1
                    gate["controller"]["controllers"].append({"id":gate["controller"]["id"] - 1})
                    gate["controller"]["controllers"].append({"id":gate["controller"]["id"] - 2})
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                    gate["controller"]["controllers"].clear()
                    gate["controller"]["id"] += 1
                    switch["controller"]["id"] = gate["controller"]["id"]
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(switch))
                    switch["controller"]["controllers"][0]["id"] += 4
                    gate["controller"]["id"] += 1
                    switch["pos"]["y"] += 1
                    gate["pos"]["z"] -= 1
                    gate["pos"]["x"] += 1
                    gate["pos"]["y"] += 1
                    blank += '-'
                gate["pos"]["y"] = 0
                gate["pos"]["x"] -= 2
            elif line[0] == ".o":       #         ________outputs
                outputs = int(line[1])
                outputs_stats = []
                if minimization_type == 1:
                    gate["controller"]["mode"] = 0
                elif minimization_type == 2:
                    gate["controller"]["mode"] = 3
                else:
                    gate["controller"]["mode"] = 1
                gate["color"] = "E2DB13"
                for i in range(0, outputs):
                    outputs_stats.append(0)
                    if i in output_splits:
                        gate["pos"]["x"] -= 1
                        gate["pos"]["y"] = 0
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                    gate["controller"]["id"] += 1
                    gate["pos"]["y"] += 1
                gate["pos"]["x"] = 0
                gate["pos"]["y"] = 0
                gate["color"] = "DF7F01"
                if minimization_type == 1:
                    gate["controller"]["mode"] = 1
                    for i in range (inputs * 4, inputs * 4 + outputs):
                        blueprint["bodies"][0]["childs"][i]["controller"]["mode"] = 0
                else:
                    gate["controller"]["mode"] = 0
                    if minimization_type == 2:
                        for i in range (inputs * 4, inputs * 4 + outputs):
                            blueprint["bodies"][0]["childs"][i]["controller"]["mode"] = 2
                mask_bool = False
            elif line[0] == ".p":
                print(',', line[1], "gates to build...", end='')
            elif line[0] == ".e":
                continue
            elif line[0][0] != '.':       #            ________cubes
                gate["controller"]["controllers"].clear()
                if line[0] == blank:
                    blueprint["bodies"][0]["childs"][0 + mask_fix * 2]["controller"]["controllers"].append({"id":copy.copy(gate["controller"]["id"])})
                    blueprint["bodies"][0]["childs"][1 + mask_fix * 2]["controller"]["controllers"].append({"id":copy.copy(gate["controller"]["id"])})
                    temp = gate["controller"]["mode"]
                    gate["controller"]["mode"] = 1
                    for i in range(outputs - 1, -1, -1):    #   outputs
                        if line[1][i] == '1':
                            gate["controller"]["controllers"].append({"id":outputs - i - 1 + inputs * 4})
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                    gate["controller"]["mode"] = temp
                    mask_bool = True
                    #print("\nIgnore this", line[1])
                else:
                    for i in range(0, inputs):    #   inputs
                        if line[0][i] != '-':
                            if line[0][i] == '1' and minimization_type != 1 or line[0][i] == '0' and minimization_type == 1:
                                if inputs_stats[i] == 255:
                                    print(f"Input {inputs - i} exceeded 255 output connections")    
                                inputs_stats[i] += 1
                                blueprint["bodies"][0]["childs"][((inputs - i - 1 + aBits) % inputs) * 4]["controller"]["controllers"].append({"id":copy.copy(gate["controller"]["id"])})
                            if line[0][i] == '0' and minimization_type != 1 or line[0][i] == '1' and minimization_type == 1:
                                if inputs_stats[i + 1] == 255:
                                    print(f"Input {inputs - i} inverted exceeded 255 output connections")
                                inputs_stats[i + 1] += 1
                                blueprint["bodies"][0]["childs"][((inputs - i - 1 + aBits) % inputs) * 4 + 1]["controller"]["controllers"].append({"id":copy.copy(gate["controller"]["id"])})
                    for i in range(outputs - 1, -1, -1):    #   outputs
                        if line[1][i] == '1':
                            if outputs_stats[i] == 255:
                                print(f"Output {outputs - i} exceeded 255 input connections")    
                            outputs_stats[i] += 1
                            gate["controller"]["controllers"].append({"id":outputs - i - 1 + inputs * 4})
                    blueprint["bodies"][0]["childs"].append(copy.deepcopy(gate))
                gate["controller"]["id"] += 1
                gate["pos"][first_coordinate] += 1
                if not length_fill:
                    if gate["pos"]["x"] == length:
                        gate["pos"]["x"] = 0
                        gate["pos"]["y"] += 1
                        if gate["pos"]["y"] == width:
                            gate["pos"]["x"] = 0
                            gate["pos"]["y"] = 0
                            gate["pos"]["z"] += 1
                elif gate["pos"]["y"] == width:
                    gate["pos"]["y"] = 0
                    gate["pos"]["z"] += 1
                    if gate["pos"]["z"] == length:
                        gate["pos"]["y"] = 0
                        gate["pos"]["z"] = 0
                        gate["pos"]["x"] += 1
    if inputs_stats:
        if mask_fix >= len(inputs_stats) // 2:
            print("\nBad mask_fix value")
        elif mask_bool and (inputs_stats[mask_fix * 2] == 255 and inputs_stats[mask_fix * 2 + 1] <= 255 or inputs_stats[mask_fix * 2] <= 255 and inputs_stats[mask_fix * 2 + 1] == 255):
            print("\nIf you see this message try changing the value mask_fix to a different input")
    if not use_custom_path:
        blueprint_path = ".."
    with open(blueprint_path + "/blueprint.json", "w") as blueprintjson:
        blueprintjson.write(json.dumps(blueprint, separators=(',', ':')))
    print("\nFinished")


import math

import subprocess

import json
import copy

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from idlelib.tooltip import Hovertip
from multiprocessing import Process, Queue


def save_config(filename_str):
    try:
        with open("Configs/" + filename_str, "w") as cfg:
            print(aBits_var.get(),
            bBits_var.get(),
            maxValueA_var.get(),
            maxValueB_var.get(),
            operation_widget['values'].index(operation_widget.get()),
            zInverted_var.get(),
            custom_input_var.get(),
            external_pla_var.get(),
            minimization_type_widget['values'].index(minimization_type_widget.get()),
            exact_var.get(),
            fast_var.get(),
            single_output_var.get(),
            single_output_both_var.get(),
            output_phase_optimization_all_var.get(),
            strong_var.get(),
            Quality_var.get(),
            Cubes_var.get(),
            manual_flags_var.get().replace(",", ""),
            width_var.get(),
            length_var.get(),
            length_fill_var.get(),
            file=cfg, sep=',')
        configs = []
        for file in os.listdir("Configs"):
            configs.append(file)
        filename_widget['values'] = configs
        print("Saved", filename_str)
    except (FileNotFoundError, IOError):
        print("Invalid file name")

def load_config(filename_str):
    if filename_str.strip() != "":
        if os.path.isfile("Configs/" + filename_str):
            with open("Configs/" + filename_str, "r") as cfg:
                config_data = cfg.readline().strip('\n').split(',')
                if len(config_data) < 21:
                    print("Error reading the config file")
                    return
                aBits_var.set(config_data[0])
                bBits_var.set(config_data[1])
                maxValueA_var.set(config_data[2])
                maxValueB_var.set(config_data[3])
                operation_widget.current(int(config_data[4]))
                zInverted_var.set(config_data[5] == 'True')
                custom_input_var.set(config_data[6])
                external_pla_var.set(config_data[7] == 'True')
                minimization_type_widget.current(int(config_data[8]))
                exact_var.set(config_data[9] == 'True')
                fast_var.set(config_data[10] == 'True')
                single_output_var.set(config_data[11] == 'True')
                single_output_both_var.set(config_data[12] == 'True')
                output_phase_optimization_all_var.set(config_data[13] == 'True')
                strong_var.set(config_data[14] == 'True')
                Quality_var.set(config_data[15])
                Cubes_var.set(config_data[16])
                manual_flags_var.set(config_data[17])
                width_var.set(config_data[18])
                length_var.set(config_data[19])
                length_fill_var.set(config_data[20] == 'True')
            external_pla_func()
            minimization_type_func()
            fill_choice()
            print("Loaded", filename_str)
        else:
            print("No such file in Configs folder")

def delete_config(filename_str):
    if os.path.isfile("Configs/" + filename_str):
        os.remove("Configs/" + filename_str)
        configs = []
        for file in os.listdir("Configs"):
            configs.append(file)
        filename_widget.set('')
        filename_widget['values'] = configs
        print("Deleted", filename_str)

def external_pla_func():
    if external_pla_var.get():
        aBits_label.config(state="disabled")
        aBits_widget.config(state="disabled")
        maxValueA_label.config(state="disabled")
        maxValueA_widget.config(state="disabled")
        maxValueB_label.config(state="disabled")
        maxValueB_widget.config(state="disabled")
        bBits_label.config(state="disabled")
        bBits_widget.config(state="disabled")
        operation_label.config(state="disabled")
        operation_widget.config(state="disabled")
        zInverted_widget.config(state="disabled")
        custom_input_label.config(state="disabled")
        custom_input_widget.config(state="disabled")
    else:
        aBits_label.config(state="normal")
        aBits_widget.config(state="normal")
        bBits_label.config(state="normal")
        bBits_widget.config(state="normal")
        maxValueA_label.config(state="normal")
        maxValueA_widget.config(state="normal")
        maxValueB_label.config(state="normal")
        maxValueB_widget.config(state="normal")
        operation_label.config(state="normal")
        operation_widget.config(state="readonly")
        zInverted_widget.config(state="normal")
        custom_input_label.config(state="normal")
        custom_input_widget.config(state="normal")

def minimization_type_func(event=None):
    index = minimization_type_widget['values'].index(minimization_type_widget.get())
    if index < 2:
        espresso_flags_label.config(state="normal")
        exact_widget.config(state="normal")
        fast_widget.config(state="normal")
        single_output_widget.config(state="normal")
        single_output_both_widget.config(state="normal")
        output_phase_optimization_all_widget.config(state="normal")
        strong_widget.config(state="normal")
        manual_flags_label.config(state="normal")
        manual_flags_widget.config(state="normal")
        exorcism_options_label.config(state="disabled")
        quality_label.config(state="disabled")
        Quality_widget.config(state="disabled")
        cubes_label.config(state="disabled")
        Cubes_widget.config(state="disabled")
    elif index == 2:
        espresso_flags_label.config(state="disabled")
        exact_widget.config(state="disabled")
        fast_widget.config(state="disabled")
        single_output_widget.config(state="disabled")
        single_output_both_widget.config(state="disabled")
        output_phase_optimization_all_widget.config(state="disabled")
        strong_widget.config(state="disabled")
        manual_flags_label.config(state="disabled")
        manual_flags_widget.config(state="disabled")
        exorcism_options_label.config(state="normal")
        quality_label.config(state="normal")
        Quality_widget.config(state="normal")
        cubes_label.config(state="normal")
        Cubes_widget.config(state="normal")
    else:
        espresso_flags_label.config(state="disabled")
        exact_widget.config(state="disabled")
        fast_widget.config(state="disabled")
        single_output_widget.config(state="disabled")
        single_output_both_widget.config(state="disabled")
        output_phase_optimization_all_widget.config(state="disabled")
        strong_widget.config(state="disabled")
        manual_flags_label.config(state="disabled")
        manual_flags_widget.config(state="disabled")
        exorcism_options_label.config(state="disabled")
        quality_label.config(state="disabled")
        Quality_widget.config(state="disabled")
        cubes_label.config(state="disabled")
        Cubes_widget.config(state="disabled")

def fill_choice():
    if length_fill_var.get():
        height_label.grid()
        length_label.grid_remove()
    else:
        length_label.grid()
        height_label.grid_remove()

def use_custom_path_func():
    if use_custom_path_var.get():
        blueprint_path_widget.config(state="normal")
    else:
        blueprint_path_widget.config(state="disabled")

def choosebpp(event=None):
    if use_custom_path_var.get():
        folder = filedialog.askdirectory(
                title="Select a folder for blueprint.json",
                mustexist=True,
                initialdir="."
            )
        if folder:
            blueprint_path_var.set(folder)

def start():
    global main_process, output_queue
    if main_process and main_process.is_alive():
        return
    save_blueprint_path()
    generate_widget.config(state="disabled")
    output_queue = Queue()
    main_process = Process(target=main, args=(aBits_var.get(),
        bBits_var.get(),
        maxValueA_var.get(),
        maxValueB_var.get(),
        operation_widget['values'].index(operation_widget.get()),
        zInverted_var.get(),
        custom_input_var.get(),
        external_pla_var.get(),
        minimization_type_widget['values'].index(minimization_type_widget.get()),
        exact_var.get(),
        fast_var.get(),
        single_output_var.get(),
        single_output_both_var.get(),
        output_phase_optimization_all_var.get(),
        strong_var.get(),
        Quality_var.get(),
        Cubes_var.get(),
        manual_flags_var.get().replace(",", "").split(),
        width_var.get(),
        length_var.get(),
        length_fill_var.get(),
        use_custom_path_var.get(),
        blueprint_path_var.get(), output_queue), daemon=True)
    main_process.start()
    stop_widget.config(state="enabled")
    poll_output()

def output_func(text):
    output_widget.configure(state="normal")
    output_widget.insert(tk.END, text)
    output_widget.configure(state="disabled")
    output_widget.see(tk.END)

def poll_output():
    try:
        while True:
            output_func(output_queue.get_nowait())
            output_widget.update_idletasks()
    except:
        pass
    if main_process and main_process.is_alive():
        #root.after_idle(poll_output)
        root.after(50, poll_output)
    else:
        stop()

def stop():
    global main_process
    stop_widget.config(state="disabled")
    if main_process and main_process.is_alive():
        main_process.terminate()
        main_process.join()
        output_widget.configure(state="normal")
        output_widget.insert(tk.END, "Process killed\n")
        output_widget.configure(state="disabled")
        output_widget.see(tk.END)
    generate_widget.config(state="enabled")


class QueueWriter:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass


def save_blueprint_path():
    with open("blueprint path.txt", "w") as bppfile:
        print(blueprint_path_var.get().strip('\n'), use_custom_path_var.get(), file=bppfile, sep='\n')




if __name__ == "__main__":
    os.chdir("resources")
    main_process = None
    output_queue = None
    root = tk.Tk()
    root.title("SM LUT Maker by Karaolli")
    root.iconphoto(False, tk.PhotoImage(file="icon.png"))
    root.geometry(f"590x706+{root.winfo_screenwidth() // 2 - 295}+{root.winfo_screenheight() // 2 - 353}")
    root.resizable(False, False)
    style = ttk.Style(root)
    style.configure(".", padding=(4, 4), font=("Segoe UI", 9))
    style.configure("Title.Label", padding=(4, 8), font=("Segoe UI", 13))
    style.configure("Generate.TButton", padding=(4, 8), font=("Segoe UI", 13))


    title_frame = ttk.Labelframe(root)
    title_frame.grid(row=0, sticky="we", padx=10)
    title_frame.columnconfigure(0, weight=1)
    ttk.Label(title_frame, text="Scrap Mechanic LUT Maker by Karaolli", style="Title.Label").grid(row=0, column=0)



    math_frame = ttk.Labelframe(root)
    math_frame.columnconfigure(0, weight=1)
    math_frame.columnconfigure(3, weight=1)
    math_frame.columnconfigure(7, weight=2)
    math_frame.grid(row=1, sticky="we", padx=10)

    aBits_label = ttk.Label(math_frame, text="Bits for input A:")
    aBits_label.grid(row=0, column=1)
    aBits_var = tk.IntVar()
    aBits_widget = ttk.Spinbox(math_frame, from_=0, to=255, width=3, textvariable=aBits_var)
    aBits_widget.grid(row=0, column=2)

    bBits_label = ttk.Label(math_frame, text="Bits for input B:")
    bBits_label.grid(row=1, column=1)
    bBits_var = tk.IntVar()
    bBits_widget = ttk.Spinbox(math_frame, from_=0, to=255, width=3, textvariable=bBits_var)
    bBits_widget.grid(row=1, column=2)

    maxValueA_label = ttk.Label(math_frame, text="Max value for A:")
    maxValueA_label.grid(row=0, column=4)
    maxValueA_var = tk.IntVar()
    maxValueA_widget = ttk.Spinbox(math_frame, from_=0, to=4294967295, textvariable=maxValueA_var, width=10)
    maxValueA_widget.grid(row=0, column=5)
    Hovertip(maxValueA_widget, "0 = Unlimited", hover_delay=50)

    maxValueB_label = ttk.Label(math_frame, text="Max value for B:")
    maxValueB_label.grid(row=1, column=4)
    maxValueB_var = tk.IntVar()
    maxValueB_widget = ttk.Spinbox(math_frame, from_=0, to=4294967295, textvariable=maxValueB_var, width=10)
    maxValueB_widget.grid(row=1, column=5)
    Hovertip(maxValueB_widget, "0 = Unlimited", hover_delay=50)

    operation_label = ttk.Label(math_frame, text="Operation:")
    operation_label.grid(row=2, column=1, sticky="e")
    operation_widget = ttk.Combobox(math_frame, values=operation_names, width=20, state="readonly")
    operation_widget.current(0)
    operation_widget.grid(row=2, column=2, columnspan=3, sticky="w")

    zInverted_var = tk.BooleanVar()
    zInverted_widget = ttk.Checkbutton(math_frame, text="Include inverted outputs", variable=zInverted_var)
    zInverted_widget.grid(row=2, column=4, columnspan=4)

    custom_input_label = ttk.Label(math_frame, text="Custom input:")
    custom_input_label.grid(row=1, column=6, padx=8)
    custom_input_var = tk.IntVar()
    custom_input_widget = ttk.Spinbox(math_frame, from_=-2147483648, to=2147483647, textvariable=custom_input_var, width=8)
    custom_input_widget.grid(row=1, column=7, sticky="w")

    external_pla_var = tk.BooleanVar()
    external_pla_widget = ttk.Checkbutton(math_frame, text="Read truth table\nfrom truth.pla", variable=external_pla_var, command=lambda: external_pla_func()).grid(row=0, column=6, columnspan=2)



    minimization_frame = ttk.Labelframe(root)
    minimization_frame.grid(row=2, sticky="we", padx=10)

    minimization_type_label = ttk.Label(minimization_frame, text="Minimization type:")
    minimization_type_label.grid(row=0, column=0)
    minimization_type_widget = ttk.Combobox(minimization_frame, values=["Sum of Products", "Product of Sums", "Exclusive Sum of Products", "Don't minimize"], state="readonly")
    minimization_type_widget.bind("<<ComboboxSelected>>", minimization_type_func)
    minimization_type_widget.current(0)
    minimization_type_widget.grid(row=0, column=1)

    espresso_flags_label = ttk.Label(minimization_frame, text="Espresso flags:")
    espresso_flags_label.grid(row=0, column=2, columnspan=2)

    exact_var = tk.BooleanVar()
    exact_widget = ttk.Checkbutton(minimization_frame, text="exact", variable=exact_var)
    exact_widget.grid(row=1, column=2, sticky="w")
    fast_var = tk.BooleanVar()
    fast_widget = ttk.Checkbutton(minimization_frame, text="fast", variable=fast_var)
    fast_widget.grid(row=1, column=3, sticky="w")
    single_output_var = tk.BooleanVar()
    single_output_widget = ttk.Checkbutton(minimization_frame, text="single output", variable=single_output_var)
    single_output_widget.grid(row=2, column=2, sticky="w")
    single_output_both_var = tk.BooleanVar()
    single_output_both_widget = ttk.Checkbutton(minimization_frame, text="single output both", variable=single_output_both_var)
    single_output_both_widget.grid(row=2, column=3, sticky="w")
    output_phase_optimization_all_var = tk.BooleanVar()
    output_phase_optimization_all_widget = ttk.Checkbutton(minimization_frame, text="output phase optimization", variable=output_phase_optimization_all_var)
    output_phase_optimization_all_widget.grid(row=3, column=2)
    strong_var = tk.BooleanVar()
    strong_widget = ttk.Checkbutton(minimization_frame, text="strong", variable=strong_var)
    strong_widget.grid(row=3, column=3, sticky="w")

    exorcism_options_label = ttk.Label(minimization_frame, text="Exorcism options:")
    exorcism_options_label.grid(row=1, column=0, columnspan=2)

    quality_label = ttk.Label(minimization_frame, text="Quality:")
    quality_label.grid(row=2, column=0, sticky="e")
    Quality_var = tk.IntVar()
    Quality_widget = ttk.Spinbox(minimization_frame, from_=0, to=32767, width=8, textvariable=Quality_var)
    Quality_widget.grid(row=2, column=1, sticky="w")
    cubes_label = ttk.Label(minimization_frame, text="Cubes:")
    cubes_label.grid(row=3, column=0, sticky="e")
    Cubes_var = tk.IntVar()
    Cubes_var.set(20000)
    Cubes_widget = ttk.Spinbox(minimization_frame, from_=20000, to=2147483647, width=8, textvariable=Cubes_var)
    Cubes_widget.grid(row=3, column=1, sticky="w")

    manual_flags_label = ttk.Label(minimization_frame, text="Manual espresso flags:")
    manual_flags_label.grid(row=4, column=0)
    manual_flags_var = tk.StringVar()
    manual_flags_widget = ttk.Entry(minimization_frame, textvariable=manual_flags_var)
    manual_flags_widget.grid(row=4, column=1, columnspan=3, sticky="we")

    minimization_type_func()


    dimensions_frame = ttk.Labelframe(root)
    dimensions_frame.grid(row=3, sticky="we", padx=10)
    dimensions_frame.columnconfigure(0, weight=1)
    dimensions_frame.columnconfigure(7, weight=1)

    ttk.Label(dimensions_frame, text="Width:").grid(row=0, column=1)
    width_var = tk.IntVar()
    width_var.set(1)
    width_widget = ttk.Spinbox(dimensions_frame, from_=1, to=32767, textvariable=width_var, width = 5)
    width_widget.grid(row=0, column=2)

    length_label = ttk.Label(dimensions_frame, text="Length:", width=7)
    length_label.grid(row=0, column=3)
    height_label = ttk.Label(dimensions_frame, text="Height:", width=7)
    height_label.grid(row=0, column=3)
    height_label.grid_remove()
    length_var = tk.IntVar()
    length_var.set(1)
    length_widget = ttk.Spinbox(dimensions_frame, from_=1, to=32767, textvariable=length_var, width = 5)
    length_widget.grid(row=0, column=4)

    length_fill_var = tk.BooleanVar()
    ttk.Radiobutton(dimensions_frame, text="Height fill", variable=length_fill_var, value=0, command=fill_choice).grid(row=0, column=5, padx=6)
    ttk.Radiobutton(dimensions_frame, text="Length fill", variable=length_fill_var, value=1, command=fill_choice).grid(row=0, column=6, padx=6)



    config_frame = ttk.Labelframe(root)
    config_frame.grid(row=4, sticky="we", padx=10)
    config_frame.columnconfigure(4, weight=1)

    configs = []
    for file in os.listdir("Configs"):
        configs.append(file)

    ttk.Label(config_frame, text="Config file name:").grid(row=0, column=0)

    filename_widget = ttk.Combobox(config_frame, values=configs)
    filename_widget.grid(row=0, column=1, pady=10)
        
    ttk.Button(config_frame, text="Save config", command=lambda:save_config(filename_widget.get()), width=14).grid(row=0, column=2)
    ttk.Button(config_frame, text="Load config", command=lambda:load_config(filename_widget.get()), width=14).grid(row=0, column=3)
    ttk.Button(config_frame, text="Delete config", command=lambda:delete_config(filename_widget.get()), width=14).grid(row=0, column=4, sticky="e")



    blueprint_path_frame = ttk.Labelframe(root)
    blueprint_path_frame.grid(row=5, sticky="we", padx=10)

    use_custom_path_var = tk.BooleanVar()
    use_custom_path_chk = ttk.Checkbutton(blueprint_path_frame, text="Custom save location", variable=use_custom_path_var, command=lambda: use_custom_path_func())
    use_custom_path_chk.grid(row=0, column=0)

    blueprint_path_frame.columnconfigure(1, weight=1)
    blueprint_path_var = tk.StringVar()
    blueprint_path_widget = ttk.Entry(blueprint_path_frame, textvariable=blueprint_path_var)
    blueprint_path_widget.grid(row=0, column=1, sticky="we", pady=4)

    blueprint_path_widget.bind("<Button-1>", choosebpp)

    try:
        with open("blueprint path.txt", "r") as bppfile:
                blueprint_path_var.set(bppfile.readline().strip('\n'))
                use_custom_path_var.set(bppfile.readline().strip('\n') == 'True')
    except FileNotFoundError:
        pass
    use_custom_path_func()

    generate_widget = ttk.Button(root, text="Generate", command=start, style="Generate.TButton")
    generate_widget.grid(row=6, pady=4)

    stop_widget = ttk.Button(root, text="Stop", command=stop, state="disabled")
    stop_widget.grid(row=6, column=0, padx=10, sticky="e")

    output_widget = scrolledtext.ScrolledText(root, wrap="word", width=10, height=8, state="disabled")
    output_widget.grid(row=7, padx=10, pady=4, sticky="we")
    
    sys.stdout.write = output_func
    sys.stderr.write = output_func

    if "autoload" in configs:
        load_config("autoload")
        filename_widget.set("autoload")


    if not manual:
        root.mainloop()
    else:
        main(1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20000, [], 0, 0, 1, 1, "", None)