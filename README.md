### A program for making two-step lookup table blueprints for Scrap Mechanic.

## Truth tables
You can choose the function that the inputs will follow, as well as define your own in the source file.  
You can limit the input values that the LUT should expect, above which it will not give correct values.  
You can also input your own truth.pla file that should be located in the root folder.  

Define your own operations in the `operations()` function, and the length of the output in `operation_lengths()`.  
To mark some combinations of inputs as 'don't care' make your function return "skip".  
You can also use the `dont_care()` function, or copy code from it for marking only certain outputs.  
Don't forget to name your operations in the `operation_names` list at the start of the file.  

## Minimization
Sum of Products (SOP) minimization will result in a AND -> OR circuit.  
Product of Sums (POS)  --  OR -> AND  
Exclusive Sum of Products (ESOP)  --  AND -> XOR  

For SOP and POS forms the Espresso algorithm is used. In the program you can apply various arguments that influence the way the function is finimized.  
For details about specific arguments, see the `help` folder.  

ESOP minimization is done using EXORCISM-4 from Berkeley's ABC.  

## Building
If you need, you can also modify the `input_splits` and `output_splits` lists to change how input and output rows of gates are split, for example if you make a function that takes in 3 numbers.  

If you get a message that an input or output exceeded 255 connections, the circuit most likely won't function as intended.  
If you only get such message for inputs, but not for outputs, please let me know.  

### Other
The program allows for saving and loading of configurations. A file with the name `autoload` gets loaded on startup of the program if it exists.  


If you have encountered a bug or have a suggestion, I'm open to any form of feedback.  