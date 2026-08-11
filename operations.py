import math

operation_names = ["a + b", "a - b", "a * b", "a >= b", "a * b >> x", "a * b & (1 << x) - 1", "1/a", "Sin", "Cos"]

def operations(a, b, aBits, bBits, x, operation, powZbits, zBits):   # to mark the entire output as don't care use   return "skip"
        operation_name = operation_names[operation]
        match operation_name:
            case "a + b":
                z = a + b
            case "a - b":
                z = a - b
                if z < 0:
                    z += powZbits
            case "a * b":
                z = a * b
            case "a >= b":
                z = (a >= b)
            case "a * b >> x":
                z = a * b >> x
            case "a * b & (1 << x) - 1":    # a * b & (1 << x) - 1
                if a * b > (1 << x) - 1: return "skip"
                z = a * b & (1 << x) - 1
            case "1/a":
                #if a != 0:
                #    if a >= 8 << x:
                #        return dont_care(a, zBits, operation)
                #    z = float_to_bin(16/a, x, powZbits)
                #else: z = 0
                if a >= 8 << x or a <= 2:
                    return dont_care(a, zBits, operation)
                z = float_to_bin(16/a, x, powZbits)
            case "Sin":
                c = math.sin(2*math.pi * a/(1 << aBits))
                z = float_to_bin(c, x, powZbits)
            case "Cos":
                c = math.cos(2*math.pi * a/(1 << aBits))
                z = float_to_bin(c, x, powZbits)


        return z

def operation_lengths(aBits, bBits, x, maxValueA, maxValueB, operation):   #     define the length of the output here.  if you want a specific amount of bits do  maxValueZ = 1 << your_number - 1
    operation_name = operation_names[operation]
    match operation_name:
        case "a + b":
            maxValueZ = maxValueA + maxValueB
        case "a - b":
            maxValueZ = maxValueA
        case "a * b":
            maxValueZ = maxValueA * maxValueB
        case "a >= b":
            maxValueZ = 1
        case "a * b >> x":
            maxValueZ = maxValueA * maxValueB >> x
        case "a * b & (1 << x) - 1":
            maxValueZ = (1 << x) - 1
        case "1/a":
            maxValueZ = (16 << x) - 1
        case "Sin":
            maxValueZ = (4 << x + 2) - 1
        case "Cos":
            maxValueZ = (4 << x + 2) - 1
        case _:
            print("Define how many output bits you need in the `operation_lengths` function.")

    return maxValueZ

mask_fix = 0

def dont_care(z, zBits, operation):
    string = ""
    zbin = format(z, f'0{zBits}b')

    operation_name = operation_names[operation]
    match operation_name:
        case "a * b >> x":
            for i in range(zBits // 2):
                string += '-'
            for i in range(zBits // 2, zBits):
                string += zbin[i]
        case "1/a":
            string += '1'
            for i in range(1, zBits):
                string += '-'
        case _:
            print("Operation not found in the `dont_care` function.")
    return string

def float_to_bin(number, precision: int, powZbits):
    v = round(number * (1 << precision))
    if v < 0:
        v += powZbits
    return v