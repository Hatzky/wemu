from tests.flexo_tests import *
from tests.gitm_tests import *
import time
import struct
from random import randint

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def log_timing_result(gate_name: str, avg_time_per_gate: float, total_iterations: int, filename: str = "output/timing_results.txt"):
    """Log timing results to file."""
    with open(filename, "a") as f:
        f.write(f"{gate_name},{avg_time_per_gate:.9f},{total_iterations}\n")

def time_gate_bulk(
    gate_fn, 
    gate_name: str,
    tot_trials: int = 1000000,
    input_bits: int = 2,
    expected_fn=None
) -> None:
    """
    Generic function to time gate operations over many iterations.
    
    Args:
        gate_fn: The gate function to test
        gate_name: Name for display purposes
        tot_trials: Number of iterations to run
        input_bits: Number of input bits to extract from seed
        expected_fn: Function to compute expected result (for validation)
    """
    def gate_fn_with_error_codes(seed: int) -> int:
        """
        Gate function that returns error codes like the hardware:
        0 = correct result
        2 = detected error (we assume this never happens in emulation)
        other = undetected error
        """
        # Extract inputs from seed
        inputs = [(seed >> i) & 1 for i in range(input_bits)]
        
        # Get emulated result
        result = gate_fn(*inputs, debug=False)
        
        # Validate if expected function provided
        if expected_fn:
            expected = expected_fn(*inputs)
            if result == expected:
                return 0  # Correct
            else:
                return 1  # Undetected error
        else:
            return 0  # Assume correct if no validation
    
    tot_correct_counts = 0
    tot_detected_counts = 0
    tot_error_counts = 0
    
    # Start timing
    start_time = time.perf_counter_ns()
    
    for seed in range(tot_trials):
        result = gate_fn_with_error_codes(seed)
        
        # Use exact same logic as hardware
        if result == 0:
            tot_correct_counts += 1
        elif result & 2:  # Check if bit 1 is set
            tot_detected_counts += 1
        else:
            tot_error_counts += 1
    
    # End timing
    end_time = time.perf_counter_ns()
    tot_ns = end_time - start_time
    tot_s = tot_ns / 1_000_000_000
    
    print(f"=== {gate_name} gate (emulated) ===")
    print(f"Accuracy: {(tot_correct_counts / tot_trials * 100):.5f}%, ", end="")
    print(f"Error detected: {(tot_detected_counts / tot_trials * 100):.5f}%, ", end="")
    print(f"Undetected error: {(tot_error_counts / tot_trials * 100):.5f}%")
    
    avg_s = tot_s / tot_trials
    print(f"Time usage per run: {avg_s:.9f} s")
    print(f"Total seconds: {tot_s:.6f} s")
    print(f"over {tot_trials} iterations.")

    # Log to file
    log_timing_result(gate_name, avg_s, tot_trials)

# -------------------------------------------------------------------
# GITM timing tests
# -------------------------------------------------------------------

def time_gitm_assign(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_assign,
        gate_name="GITM ASSIGN",
        tot_trials=tot_trials,
        input_bits=1,
        expected_fn=lambda in1: in1
    )

def time_gitm_and(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_and,
        gate_name="GITM AND",
        tot_trials=tot_trials,
        input_bits=2,
        expected_fn=lambda in1, in2: in1 and in2
    )

def time_gitm_or(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_or,
        gate_name="GITM OR",
        tot_trials=tot_trials,
        input_bits=2,
        expected_fn=lambda in1, in2: in1 or in2
    )

def time_gitm_not(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_not,
        gate_name="GITM NOT",
        tot_trials=tot_trials,
        input_bits=1,
        expected_fn=lambda in1: 1 - in1
    )

def time_gitm_nand(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_nand,
        gate_name="GITM NAND",
        tot_trials=tot_trials,
        input_bits=2,
        expected_fn=lambda in1, in2: 1 - (in1 and in2)
    )

def time_gitm_xor(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_xor,
        gate_name="GITM XOR",
        tot_trials=tot_trials,
        input_bits=2,
        expected_fn=lambda in1, in2: in1 ^ in2
    )

def time_gitm_mux(tot_trials):
    time_gate_bulk(
        gate_fn=emulate_gitm_mux,
        gate_name="GITM MUX",
        tot_trials=tot_trials,
        input_bits=3,
        expected_fn=lambda sel, in1, in2: in2 if sel else in1
    )

# -------------------------------------------------------------------
# Flexo timing tests
# -------------------------------------------------------------------

def time_flexo_and(tot_trials: int = 1000000) -> None:
    """Time Flexo AND gate over multiple iterations."""
    print(f"\n=== Flexo AND Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (2 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_and(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo AND Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo AND", avg_time, tot_trials)

def time_flexo_or(tot_trials: int = 1000000) -> None:
    """Time Flexo OR gate over multiple iterations."""
    print(f"\n=== Flexo OR Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (2 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_or(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo OR Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo OR", avg_time, tot_trials)

def time_flexo_not(tot_trials: int = 1000000) -> None:
    """Time Flexo NOT gate over multiple iterations."""
    print(f"\n=== Flexo NOT Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random input (1 bit)
        a = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_not(a, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo NOT Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo NOT", avg_time, tot_trials)

def time_flexo_nand(tot_trials: int = 1000000) -> None:
    """Time Flexo NAND gate over multiple iterations."""
    print(f"\n=== Flexo NAND Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (2 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_nand(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo NAND Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo NAND", avg_time, tot_trials)

def time_flexo_xor(tot_trials: int = 1000000) -> None:
    """Time Flexo XOR gate over multiple iterations."""
    print(f"\n=== Flexo XOR Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (2 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_xor(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo XOR Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo XOR", avg_time, tot_trials)

def time_flexo_xor3(tot_trials: int = 1000000) -> None:
    """Time Flexo XOR3 gate over multiple iterations."""
    print(f"\n=== Flexo XOR3 Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (3 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        c = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_xor3(a, b, c, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo XOR3 Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo XOR3", avg_time, tot_trials)

def time_flexo_xor4(tot_trials: int = 1000000) -> None:
    """Time Flexo XOR4 gate over multiple iterations."""
    print(f"\n=== Flexo XOR4 Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (4 bits)
        a = randint(0, 1)
        b = randint(0, 1)
        c = randint(0, 1)
        d = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_xor4(a, b, c, d, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo XOR4 Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo XOR4", avg_time, tot_trials)

def time_flexo_mux(tot_trials: int = 1000000) -> None:
    """Time Flexo MUX gate over multiple iterations."""
    print(f"\n=== Flexo MUX Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs (3 bits: sel, in1, in2)
        sel = randint(0, 1)
        in1 = randint(0, 1)
        in2 = randint(0, 1)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_mux(sel, in1, in2, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10,000 iterations
        if (i + 1) % 10000 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo MUX Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per gate: {avg_time:.9f} s")
    print(f"Average time per gate (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo MUX", avg_time, tot_trials)

def time_flexo_alu(tot_trials: int = 1000000) -> None:
    """Time Flexo ALU over multiple iterations."""
    print(f"\n=== Flexo ALU Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random inputs
        x_data = randint(0, 15)      # 4 bits
        y_data = randint(0, 15)      # 4 bits
        control_data = randint(0, 63) # 6 bits
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_alu(x_data, y_data, control_data, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 100 iterations
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo ALU Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per ALU operation: {avg_time:.9f} s")
    print(f"Average time per ALU operation (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo ALU", avg_time, tot_trials)

def time_flexo_adder8(tot_trials: int = 1000000) -> None:
    """Time Flexo 8-bit adder over multiple iterations."""
    print(f"\n=== Flexo 8-bit ADDER Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random 8-bit inputs
        a = randint(0, 255)
        b = randint(0, 255)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_adder8(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 100 iterations
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo 8-bit ADDER Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per addition: {avg_time:.9f} s")
    print(f"Average time per addition (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo 8-bit ADDER", avg_time, tot_trials)

def time_flexo_adder16(tot_trials: int = 1000000) -> None:
    """Time Flexo 16-bit adder over multiple iterations."""
    print(f"\n=== Flexo 16-bit ADDER Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random 16-bit inputs
        a = randint(0, 65535)
        b = randint(0, 65535)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_adder16(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 100 iterations
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo 16-bit ADDER Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per addition: {avg_time:.9f} s")
    print(f"Average time per addition (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo 16-bit ADDER", avg_time, tot_trials)

def time_flexo_adder32(tot_trials: int = 1000000) -> None:
    """Time Flexo 32-bit adder over multiple iterations."""
    print(f"\n=== Flexo 32-bit ADDER Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random 32-bit inputs
        a = randint(0, 0xFFFFFFFF)
        b = randint(0, 0xFFFFFFFF)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_adder32(a, b, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo 32-bit ADDER Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per addition: {avg_time:.9f} s")
    print(f"Average time per addition (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo 32-bit ADDER", avg_time, tot_trials)

def time_flexo_sha1_round(tot_trials: int = 1000) -> None:
    """Time Flexo SHA-1 round over multiple iterations."""
    print(f"\n=== Flexo SHA-1 Round Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random test inputs
        state = [randint(0, 0xFFFFFFFF) for _ in range(5)]
        w = randint(0, 0xFFFFFFFF)
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_sha1_round(state, w, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo SHA-1 Round Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per SHA-1 round: {avg_time:.9f} s")
    print(f"Average time per SHA-1 round (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo SHA-1 Round", avg_time, tot_trials)

def time_flexo_aes_round(tot_trials: int = 1000) -> None:
    """Time Flexo AES round over multiple iterations."""
    print(f"\n=== Flexo AES Round Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random test inputs
        input_block = [randint(0, 255) for _ in range(16)]
        key_block = [randint(0, 255) for _ in range(16)]
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_aes_round(input_block, key_block, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo AES Round Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per AES round: {avg_time:.9f} s")
    print(f"Average time per AES round (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo AES Round", avg_time, tot_trials)

def time_flexo_simon32(tot_trials: int = 50) -> None:
    """Time Flexo SIMON32 block over multiple iterations."""
    print(f"\n=== Flexo SIMON32 Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random test inputs
        input_block = [randint(0, 255) for _ in range(4)]   # 4-byte (32-bit) block
        key_block = [randint(0, 255) for _ in range(8)]     # 8-byte (64-bit) key
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_simon32(input_block, key_block, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo SIMON32 Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per SIMON32 block: {avg_time:.9f} s")
    print(f"Average time per SIMON32 block (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo SIMON32", avg_time, tot_trials)

def time_flexo_sha1_2blocks(tot_trials: int = 50) -> None:
    """Time Flexo SHA-1 2-blocks over multiple iterations."""
    print(f"\n=== Flexo SHA-1 2-blocks Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random test inputs - two 16-word (64-byte) blocks
        block1 = [randint(0, 0xFFFFFFFF) for _ in range(16)]
        block2 = [randint(0, 0xFFFFFFFF) for _ in range(16)]
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_sha1_2blocks(block1, block2, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo SHA-1 2-blocks Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per SHA-1 2-blocks: {avg_time:.9f} s")
    print(f"Average time per SHA-1 2-blocks (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo SHA-1 2-blocks", avg_time, tot_trials)

def time_flexo_aes_block(tot_trials: int = 50) -> None:
    """Time Flexo AES block over multiple iterations."""
    print(f"\n=== Flexo AES Block Average Timing ({tot_trials} iterations) ===")
    total_time = 0.0
    
    for i in range(tot_trials):
        # Generate random test inputs (16 bytes each for input and key)
        input_data = [randint(0, 255) for _ in range(16)]
        key_data = [randint(0, 255) for _ in range(16)]
        
        # Time the emulation
        start_time = time.perf_counter_ns()
        emulate_flexo_aes_block(input_data, key_data, debug=False)
        end_time = time.perf_counter_ns()
        
        tot_ns = end_time - start_time
        tot_s = tot_ns / 1_000_000_000
        total_time += tot_s
        
        # Progress update every 10 iterations
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{tot_trials} iterations...")
    
    # Calculate and display results
    avg_time = total_time / tot_trials
    print(f"\n=== Flexo AES Block Average Results ===")
    print(f"Total iterations: {tot_trials}")
    print(f"Total execution time: {total_time:.6f} s")
    print(f"Average execution time per AES block: {avg_time:.9f} s")
    print(f"Average time per AES block (nanoseconds): {avg_time * 1_000_000_000:.2f} ns")

    # Log to file
    log_timing_result("Flexo AES Block", avg_time, tot_trials)

# -------------------------------------------------------------------
# Timing test runner
# -------------------------------------------------------------------

TRIAL_COUNT_S = 1000000
TRIAL_COUNT_M = 1000
TRIAL_COUNT_S = 50

def run_all_gitm_timing_tests(tot_trials: int = 1000000) -> None:
    """Run all GITM timing tests with the specified number of trials."""
    print(f"\n{'='*50}")
    print(f"Running GITM timing tests")
    print(f"{'='*50}")
    
    # time_gitm_assign(TRIAL_COUNT_M)
    # time_gitm_and(TRIAL_COUNT_M)
    # time_gitm_or(TRIAL_COUNT_M)
    # time_gitm_not(TRIAL_COUNT_M)
    # time_gitm_nand(TRIAL_COUNT_M)
    # time_gitm_xor(TRIAL_COUNT_M)
    # time_gitm_mux(TRIAL_COUNT_M)
    
    print(f"\n{'='*50}")
    print("All GITM timing tests completed!")
    print(f"{'='*50}")

def run_all_flexo_timing_tests(tot_trials: int = 1000) -> None:
    """Run all Flexo timing tests with the specified number of trials."""
    print(f"\n{'='*50}")
    print(f"Running Flexo timing tests")
    print(f"{'='*50}")
    
    time_flexo_and(TRIAL_COUNT_M)
    time_flexo_or(TRIAL_COUNT_M)
    time_flexo_not(TRIAL_COUNT_M)
    time_flexo_nand(TRIAL_COUNT_M)
    time_flexo_xor(TRIAL_COUNT_M)
    time_flexo_xor3(TRIAL_COUNT_M)
    time_flexo_xor4(TRIAL_COUNT_M)
    time_flexo_mux(TRIAL_COUNT_M)
    time_flexo_alu(TRIAL_COUNT_M)
    time_flexo_adder8(TRIAL_COUNT_M)
    time_flexo_adder16(TRIAL_COUNT_M)
    time_flexo_adder32(TRIAL_COUNT_M)
    time_flexo_sha1_round(TRIAL_COUNT_M)
    time_flexo_aes_round(TRIAL_COUNT_M)
    time_flexo_simon32(TRIAL_COUNT_M)

    time_flexo_sha1_2blocks(50)
    time_flexo_aes_block(50)
    
    print(f"\n{'='*50}")
    print("All Flexo timing tests completed!")
    print(f"{'='*50}")

if __name__ == "__main__":
    # Time when round 67 of sha-1 2 blocks begins
    # block1 = [randint(0, 0xFFFFFFFF) for _ in range(16)]
    # block2 = [randint(0, 0xFFFFFFFF) for _ in range(16)]
    # emulate_flexo_sha1_2blocks(block1, block2, debug=False)

    run_all_gitm_timing_tests()
    run_all_flexo_timing_tests()