import os

folder_path = r"C:\Users\Gaurav Tiwari\OneDrive\Desktop\Portfolio website\photos"

files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

for file in files:
    print(file)
