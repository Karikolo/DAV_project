import os.path

import pandas as pd
import pmdarima as pm
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import sys

data_file = "../data/2020-2022/weekly-confirmed-covid-19-deaths_2020_2022_20250516.csv"
title = "COVID-19 Deaths in Canada (2020–2022) forecast"
y_column_name = 'Weekly deaths'
data_name = 'deaths'

def main():
    df = pd.read_csv(data_file, parse_dates=['Day'])
    df = df[df['Entity'] == "Canada"]
    df.set_index('Day', inplace=True)
    y = df[y_column_name]

    test_size = int(len(y) * 0.15)
    y_train = y.iloc[:-test_size]
    y_test = y.iloc[-test_size:]


    # Auto-tune SARIMA with seasonality, parameter tuning
    model = pm.arima.auto_arima(
        y_train,
        seasonal=True,
        m=14,  # quarterly seasonality
        start_p=0, max_p=3,
        start_q=0, max_q=3,
        start_P=0, max_P=2,
        start_Q=0, max_Q=2,
        d=None, D=None,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )

    print(model.summary())

    # Use the best parameters found
    order = model.order              # e.g., (1, 1, 1)
    seasonal_order = model.seasonal_order  # e.g., (1, 1, 0, 7)

    # Best parameters model
    sarimax_model = SARIMAX(
        y_train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = sarimax_model.fit()
    print(results.summary())

    # Forecast
    forecast = results.get_forecast(steps=test_size)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    # Plot
    plt.figure(figsize=(14, 6))
    # Plot historical data
    plt.plot(y_train.index, y_train, label='Training Data', color='magenta')
    # Plot actual test data
    plt.plot(y_test.index, y_test, label='Actual Test Data', color='blue')
    # Plot forecast
    plt.plot(y_test.index, forecast_mean, label='Forecast', color='orange')
    # Confidence intervals
    plt.fill_between(y_test.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='orange', alpha=0.3)

    plt.title(f"Forecast vs Actual for Last {test_size} Days")
    plt.xlabel("Date")
    plt.ylabel(f"Daily COVID-19 {data_name}")
    plt.legend()
    plt.tight_layout()
    plt.grid()
    try:
        save = sys.argv[1]
        if save!='0':
            plt.savefig(f"../plots/{data_name}_forecast_2020-22.png", dpi=300)
            print (f"../plots/{data_name}_forecast_2020-22.png")
        else:
            plt.show()
    except:
        print("Add argument '0' if you want to show interactively, '1' to save to file. Default is 0.")
        plt.show()

if __name__ == "__main__":
    main()
