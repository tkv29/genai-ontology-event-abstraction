import pm4py
import os



# input_path = os.getcwd() + "/abstracted_medication.xes"
# output_path = os.getcwd() + "/abstracted_medication.csv"
# df = pm4py.read_xes(input_path)
# df.to_csv(output_path, index=False)
# print("Conversion completed successfully")



input_path = os.getcwd() + "/abstracted_medication.xes"

df = pm4py.read_xes(input_path)
#df.rename(columns={'medication': 'extracted_medication'}, inplace=True)
df.rename(columns={'concept:name': 'abstracted_medication'}, inplace=True)
df.rename(columns={'normalized_medication': 'concept:name'}, inplace=True)
pm4py.write_xes(df, os.getcwd() + "/normalized_medication.xes")