from lib.dataprocess import *
from lib.datavis import visulization
import warnings
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    print("Please wait for processing data...")
    data_process()
    print("Data prepared done.")
    print("Start visualization...")
    # Loading Data
    dataname = "covid_usa_all_data.csv"
    df = Data(filename=dataname)
    df = df.read_data()
    app = visulization(df)
    app.run_server(debug=True)
