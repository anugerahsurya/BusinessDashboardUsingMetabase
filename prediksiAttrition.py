# === Library Dasar Python ===
import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder, OneHotEncoder

def preprocessingData(df, kolom, jenis=1, save_dir="Encoder Tersimpan", ordinal_order=None, use=False):
    os.makedirs(save_dir, exist_ok=True)
    encoder_path = os.path.join(save_dir, f"{kolom}_encoder.pkl")

    if jenis == 1:  # Label Encoding
        if use:
            with open(encoder_path, 'rb') as file:
                le = pickle.load(file)
            df[kolom] = le.transform(df[kolom])
        else:
            le = LabelEncoder()
            df[kolom] = le.fit_transform(df[kolom])
            with open(encoder_path, 'wb') as file:
                pickle.dump(le, file)
        return df, le

    elif jenis == 2:  # One Hot Encoding
        if use:
            with open(encoder_path, 'rb') as file:
                ohe = pickle.load(file)
            transformed = ohe.transform(df[[kolom]])
        else:
            ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            transformed = ohe.fit_transform(df[[kolom]])
            with open(encoder_path, 'wb') as file:
                pickle.dump(ohe, file)

        ohe_df = pd.DataFrame(transformed, columns=[f"{kolom}_{cat}" for cat in ohe.categories_[0]], index=df.index)
        df = pd.concat([df.drop(columns=[kolom]), ohe_df], axis=1)
        return df, ohe


    elif jenis == 3:  # Ordinal Encoding
        if ordinal_order is None:
            raise ValueError(f"Untuk kolom '{kolom}', 'ordinal_order' harus disediakan untuk Ordinal Encoding.")

        df[kolom] = df[kolom].astype(str)

        if use:
            with open(encoder_path, 'rb') as file:
                oe = pickle.load(file)
            df[kolom] = oe.transform(df[[kolom]])
        else:
            oe = OrdinalEncoder(categories=[ordinal_order])
            df[kolom] = oe.fit_transform(df[[kolom]])
            with open(encoder_path, 'wb') as file:
                pickle.dump(oe, file)
        return df, oe

    else:
        raise ValueError("Jenis encoding tidak valid: gunakan 1 (Label), 2 (One Hot), atau 3 (Ordinal)")

def pipelinePemrosesan(df, save_dir="Encoder Tersimpan", use=False):
    # Definisikan urutan ordinal
    urutanTravel = [
        'Non-Travel','Travel_Rarely','Travel_Frequently'
    ]

    # ====================== Ordinal Encoding ===========================
    df, _ = preprocessingData(df, 'BusinessTravel', jenis=3, ordinal_order=urutanTravel, save_dir=save_dir, use=use)
    
    # ====================== Label Encoding =============================
    label_columns = [
        'Gender','MaritalStatus','OverTime'
    ]
    for col in label_columns:
        df, _ = preprocessingData(df, col, jenis=1, save_dir=save_dir, use=use)

    # ====================== One Hot Encoding ===========================
    onehot_columns = ['Department','EducationField','JobRole']
    for col in onehot_columns:
        df, _ = preprocessingData(df, col, jenis=2, save_dir=save_dir, use=use)

    return df

def inferenceCell(input_data):
    # Load urutan kolom saat training
    with open("Encoder Tersimpan/kolomfit_attrition.pkl", "rb") as f:
        feature_order = pickle.load(f)

    # Pastikan input dalam bentuk DataFrame
    if isinstance(input_data, dict):
        input_df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        input_df = input_data.copy()
    else:
        raise ValueError("Input harus berupa dict atau DataFrame")

    # Proses preprocessing
    data_processed = pipelinePemrosesan(input_df, use=True)
    
    # Pastikan urutan kolom sesuai training
    data_processed = data_processed[feature_order]

    # Load model dan prediksi
    with open("Model Tersimpan/Model_Terbaik.pkl", "rb") as f:
        model = pickle.load(f)

    prediction = model.predict(data_processed)
    if prediction[0] == 0:
        prediksi = 'No'
    else:
        prediksi = 'Yes'
    print("Hasil Prediksi:", prediksi)
    
    return prediksi

import pandas as pd

# Load data dari Excel
data_path = "datainput.xlsx"
data = pd.read_excel(data_path)
# Ambil observasi terakhir sebagai input
input_sample = data.iloc[-1]
# Konversi ke dictionary agar sesuai dengan fungsi inferenceCell
input_dict = input_sample.to_dict()
# Panggil fungsi prediksi
hasil = inferenceCell(input_dict)



