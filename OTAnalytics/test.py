import pandas as pd

df_count = pd.read_excel(r"C:\Users\Goerner\Desktop\test1.xlsx")

print(df_count)

df_count["Datetime"] = pd.to_datetime(df_count["first_appearance_time"])
df_count = df_count.set_index("Datetime")

df_count = (
    df_count.groupby(
        [pd.Grouper(freq="5T"), "Class", "Movement", "Movement_name"], dropna=False
    )
    .size()
    .reset_index(name="counts")
)

print(df_count)
