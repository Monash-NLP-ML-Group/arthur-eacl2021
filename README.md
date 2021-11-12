# Generating Oracle for Learning Coupled Policies Using Imitation Learning

Input: 
- Synchronized alignment in the format of src-trg. You can use FastAlign for this.
- The source file, 1 sentence per line.
- The target file, 1 sentence per line.

Output:
- Oracle file of Read and Write action, 1 oracle per line.

Options:
- Can be used to generate wait-k oracle actions. For this specify `--mode wait --wait_num 3` for wait-3 for example.
- Can be used to artificially add delay to the oracle actions. For this use `--add_delay 2` to always wait 2 before start writing.
- Can be used to add eos actions as final action. Specify `--add_eos` to do so.
