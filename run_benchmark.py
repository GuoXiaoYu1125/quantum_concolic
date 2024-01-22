import subprocess
from tqdm import tqdm
import os

def run(qubtis_num, target_file, output_file, repeat_time):
    command = ['python', 'Zeus.py', '-n', str(qubtis_num), '-s', 'quantum_program', '-r', str(repeat_time), target_file]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    with open(output_file, "w") as file:
        file.write(result.stdout)
        file.write(result.stderr)


if __name__ == "__main__":
    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 1
            target_file = 'benchmark/exp_1_2/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_1_2_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=50)

    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 1
            target_file = 'benchmark/exp_1_3/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_1_3_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=75)

    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 1
            target_file = 'benchmark/exp_1_5/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_1_5_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=125)

    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 1
            target_file = 'benchmark/exp_1_10/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_1_10_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=250)

    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 2
            target_file = 'benchmark/exp_2_2/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_2_2_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=100)

    for j in range(10):
        for i in tqdm(range(40), desc="Processing", unit="iteration"):
            qubtis_num = 2
            target_file = 'benchmark/exp_2_3/quantum_program_'+str(i)+'.py'
            output_file = 'random_vector_output/output_2_3_'+str(j)+'/output_'+str(i)+'.txt'
            run(qubtis_num, target_file, output_file, repeat_time=150)


    # for i in tqdm(range(40), desc="Processing", unit="iteration"):
    #     qubtis_num = 3
    #     target_file = 'benchmark/exp_3_10/quantum_program_'+str(i)+'.py'
    #     output_file = 'random_vector_output/output_3_10/output_'+str(i)+'.txt'
    #     run(qubtis_num, target_file, output_file)

    # i = 23
    # qubtis_num = 3
    # target_file = 'benchmark/exp_3_2/quantum_program_'+str(i)+'.py'
    # output_file = 'random_vector_output/output_3_2/output_'+str(i)+'.txt'
    # run(qubtis_num, target_file, output_file)