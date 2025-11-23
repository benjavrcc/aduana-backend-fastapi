# model_monthly.py
import pandas as pd
import statsmodels.api as sm
import pickle
from pathlib import Path
from datetime import datetime

MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]

DATA_DIR = Path("data")
MODEL_PATH = DATA_DIR/"modelo_nb.pkl"

class PredictorMensual:

    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self.model = None
        self.X_cols = None

    def cargar_datos(self):
        viajes = pd.read_csv(DATA_DIR/"viajes.csv")     # 2023 + 2024
        clima  = pd.read_csv(DATA_DIR/"clima.csv")      # estacionario
        econ   = pd.read_csv(DATA_DIR/"economia.csv")   # append-only

        viajes["MES"] = pd.Categorical(viajes["MES"], categories=MESES, ordered=True)
        clima["MES"]  = pd.Categorical(clima["MES"],  categories=MESES, ordered=True)
        econ["MES"]   = pd.Categorical(econ["MES"],   categories=MESES, ordered=True)

        # usar siempre el último TCR disponible por mes
        econ_last = econ.sort_values("ANIO").groupby("MES").tail(1)

        df = (viajes
              .merge(clima, on="MES", how="left")
              .merge(econ_last[["MES","TCR"]], on="MES", how="left")
        )

        return df.dropna()

    def entrenar(self):
        df = self.cargar_datos()

        X = df[["MES","ANIO","TEMP_PROM","NIEVE_TOT","TCR"]]
        X = pd.get_dummies(X, columns=["MES"], drop_first=True)
        y = df["TOTAL_ENTRADAS"]
        
        X = sm.add_constant(X)
        model = sm.GLM(y, X, family=sm.families.NegativeBinomial()).fit()

        self.model = model
        self.X_cols = X.columns.tolist()

        with open(MODEL_PATH, "wb") as f:
            pickle.dump({"model": model, "cols": self.X_cols}, f)

    def cargar_modelo(self):
        if MODEL_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                obj = pickle.load(f)
            self.model = obj["model"]
            self.X_cols = obj["cols"]
        else:
            self.entrenar()

    def predict_month_total(self, mes:str, anio:int):
        self.cargar_modelo()

        clima = pd.read_csv(DATA_DIR/"clima.csv")
        econ  = pd.read_csv(DATA_DIR/"economia.csv")

        clim = clima[clima["MES"] == mes].iloc[0]
        econ_mes = econ[econ["MES"] == mes].sort_values("ANIO").iloc[-1]

        data = pd.DataFrame([{
            "MES": mes,
            "ANIO": anio,
            "TEMP_PROM": clim["TEMP_PROM"],
            "NIEVE_TOT": clim["NIEVE_TOT"],
            "TCR": econ_mes["TCR"]
        }])

        data = pd.get_dummies(data, columns=["MES"], drop_first=True)
        data = data.reindex(columns=[c for c in self.X_cols if c != "const"], fill_value=0)
        data = sm.add_constant(data)

        pred = float(self.model.predict(data)[0])
        return max(pred, 0)

    def predict_day_total(self, fecha_str:str):
        f = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        mes_nombre = MESES[f.month - 1]

        # mensual → E_mes
        E_mes = self.predict_month_total(mes_nombre, f.year)

        # pesos diarios
        import calendar
        dias_mes = calendar.monthrange(f.year, f.month)[1]
        dias = pd.date_range(f"{f.year}-{f.month:02d}-01", periods=dias_mes)

        df = pd.DataFrame({"FECHA": dias})
        df["DIA_MES"] = df["FECHA"].dt.day
        df["DIA_SEM"] = df["FECHA"].dt.dayofweek
        df["ES_FINDE"] = df["DIA_SEM"].isin([5,6])
        df["PESO"] = 1.0
        df.loc[df["ES_FINDE"], "PESO"] += 1
        df.loc[df["DIA_MES"] <= 5, "PESO"] += 0.5
        df.loc[df["DIA_MES"] >= 25, "PESO"] += 0.3

        df["p_dia"] = df["PESO"] / df["PESO"].sum()

        p = df[df["FECHA"].dt.date == f].iloc[0]["p_dia"]
        E_dia = E_mes * p
        return E_mes, E_dia
