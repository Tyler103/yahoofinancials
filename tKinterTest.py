from datetime import datetime, timedelta
import tkinter as tk
import sys
import time
from yahoofinancials import YahooFinancials as YF
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


DEFAULT_ARGS = 'DOGE-JPY'
MODULE_ARGS = ('yf', 'yahoofinancial', 'yahoofinancials')
HELP_ARGS = ('-h', '--help')
OUTPUT = ''
mark = '-' * 64

tick = None


def default_api(ticker):
    global OUTPUT
    global tick

    tick = YF(ticker)

    OUTPUT += '{:25s}{:,.2f}\n'.format('Current Price: ', tick.get_current_price())
    OUTPUT += '{:22s}{:,.2f}\n'.format('Current Volume: ', tick.get_current_volume())
    OUTPUT += '{:23s}{:,.2f}\n'.format('Prev Close Price: ', tick.get_prev_close_price())
    OUTPUT += '{:26s}{:,.2f}\n'.format('Open Price: ', tick.get_open_price())
    OUTPUT += '{:26s}{:,.2f}\n'.format('Daily Low: ', tick.get_daily_low())
    OUTPUT += '{:27s}{:,.2f}\n'.format('Daily High: ', tick.get_daily_high())

    try:
        r = tick._cache.keys()
    except AttributeError:
        pass

def custom_api(queries, ts):
    global OUTPUT
    yf = YF(ts[0] if 1 == len(ts) else ts)
    for q in queries:
        OUTPUT += ('%s:' % (q,)) + '\n'
        timeit(lambda: print(getattr(yf, q)()))

def help_api(queries):
    global OUTPUT
    if len(queries) == 1:
        print(__doc__ % {'scriptname': sys.argv[0], 'defaultargs': ', '.join(DEFAULT_ARGS)})
    else:
        import pydoc
        for q in queries:
            if q in MODULE_ARGS:
                OUTPUT += (pydoc.render_doc(YF, "Help on %s")) + '\n'
            elif q not in HELP_ARGS:
                OUTPUT += (pydoc.render_doc(getattr(YF, q), "Help on %s")) + '\n'


def timeit(f, *args):
    global OUTPUT
    st = time.time()
    f(*args)
    et = time.time()


def setup():
    global OUTPUT

    api = set(s for s in dir(YF) if s.startswith('get_'))
    api.update(MODULE_ARGS)
    api.update(HELP_ARGS)
    ts = sys.argv[1:]
    queries = [q for q in ts if q in api]
    ts = [t for t in ts if not t in queries] or DEFAULT_ARGS
    if [h for h in HELP_ARGS if h in queries]:
        help_api(queries)
    elif queries:
        custom_api(queries, ts)
    else:
        timeit(default_api, ts[0] if 1 == len(ts) else ts)

    text = tk.Text(root, wrap='word', font=('Times', 18))
    text.insert('insert', OUTPUT)
    text.place(x=1, y=46, width=710, height=300)
    root.update()
    OUTPUT = ''


def test_button():
    global DEFAULT_ARGS
    DEFAULT_ARGS = (first_entry.get())

    if is_valid_ticker(DEFAULT_ARGS):
        setup()
    else:
        DEFAULT_ARGS += '-' + clicked.get()
        if is_valid_ticker(DEFAULT_ARGS):
            setup()
        else:
            tk.messagebox.showinfo('Invalid Ticker', 'The option you entered is not a valid ticker. Please try again.')


def display_stock_graph():
    # stock ticker
    DEFAULT_ARGS = (first_entry.get())

    # makes the ticker a object
    ticker_data = yf.Ticker(DEFAULT_ARGS)

    # creates the boundary to extract data from
    current_day = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    current_day_data = ticker_data.history(start=current_day, end=tomorrow, interval='1m')

    # shows data in intervals of 30 minutes
    hours_data_30 = current_day_data.between_time('09:00:00', '16:00:00').resample('30T').last()

    # Create empty lists to store the time and price
    stock_times = []
    stock_prices = []

    # puts the items in their list
    for hour, price in zip(hours_data_30.index, hours_data_30['Close']):
        time = hour.strftime('%I:%M %p')
        stock_times.append(time)
        stock_prices.append(price)

    # Create a figure and add a subplot
    fig = Figure(figsize=(16, 4), dpi=100)
    grap = fig.add_subplot(111)

    # Plot the data as a line graph
    grap.plot(stock_times, stock_prices)

    # gets the current day
    fin_current_day = datetime.now().strftime('(%m-%d)')

    # Labels the graph
    _title = DEFAULT_ARGS + "'s Daily Prices " + fin_current_day
    grap.set_title(_title)
    grap.set_xlabel("Time(AM-PM)")
    grap.set_ylabel("Stock Price($)")

    # Create a canvas to display the graph in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=390)
    # end of this method


def is_valid_ticker(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info['regularMarketPrice']
        return True
    except:
        return False


# Function to toggle the visibility of the listbox when the entry widget is clicked
def toggle_dropdown(event):
    global dropdown_visible
    if dropdown_visible:
        listbox.pack_forget()
        dropdown_visible = False
    else:
        listbox.pack()
        dropdown_visible = True


# Function to update the selected options when the user makes a selection
def update_selection():
    global selected_options, dropdown_visible
    selected_options = [listbox.get(idx) for idx in listbox.curselection()]
    dropdown_entry_var.set(", ".join(selected_options))
    dropdown_visible = False
    listbox.pack_forget()

    # Checks which choices have been chosen in the
    # additional information drop down menu and
    # returns the string to be printed to the screen
    # Loops through chosen information
    # Checks for each option in dropdown, calls appropriate
    # methods and adds appropriate text for each selection
    text = ''
    for selected in selected_options:
        if selected == 'Dividend Yield':
            temp = tick.get_dividend_yield()
            if temp is None:
                temp = '--'
            text += 'Dividend Yield: {}\n'.format(temp)

        elif selected == 'Dividend Rate':
            temp = tick.get_dividend_rate()
            if temp is None:
                temp = '--'
            text += 'Dividend Rate: {}\n'.format(temp)

        elif selected == 'Yearly High':
            temp = tick.get_yearly_high()
            if temp is None:
                temp = '--'
            text += 'Yearly High: {}\n'.format(temp)

        elif selected == 'Yearly Low':
            temp = tick.get_yearly_low()
            if temp is None:
                temp = '--'
            text += 'Yearly Low: {}\n'.format(temp)

        elif selected == 'Annual Average Dividend Yield':
            temp = tick.get_annual_avg_div_yield()
            if temp is None:
                temp = '--'
            text += 'Annual Average Dividend Yield: {}\n'.format(temp)

        elif selected == '5 Year Average Dividend Yield':
            temp = tick.get_five_yr_avg_div_yield()
            if temp is None:
                temp = '--'
            text += '5 Year Average Dividend Yield: {}\n'.format(temp)

    text2 = tk.Text(root, wrap='word', font=('Times', 18))
    text2.insert('insert', text)
    # y was 46
    text2.place(x=720, y=46, width=340, height=300)
    root.update()


# Holds data for drop down menus
currency_options = [
    "USD",
    "CAD",
    "EUR"
]

additional_info = [
    "Dividend Yield",
    "Dividend Rate",
    "Yearly High",
    "Yearly Low",
    "Annual Average Dividend Yield",
    "5 Year Average Dividend Yield",
]

# BEGIN TKINTER BUILD

root = tk.Tk()
root.title("test")
root.geometry("2000x900")

first_label = tk.Label(root, text='Enter ticker here: ', font=('Times', 26))
first_label.place(x=0, y=0)

first_entry = tk.Entry(root, font=('Times', 26))
first_entry.place(x=250, y=0)

# Create Dropdown menu for currency type
clicked = tk.StringVar()  # datatype of menu text
clicked.set(currency_options[0])  # initial menu text
currency_drop = tk.OptionMenu(root, clicked, *currency_options)
currency_drop.config(height=2, width=6)
currency_drop.place(x=585, y=0)

search_bar_go_button = tk.Button(root, text='GO', command=lambda: test_button(), height=2, width=5)
search_bar_go_button.place(x=665, y=3)

# Additional information text
stock_data_label = tk.Label(root, text='Additional Information: ', font=('Times', 26))
stock_data_label.place(x=720, y=0)

# Additional Information Dropdown menu
# Create a frame to hold the dropdown widget
dropdown_frame = tk.Frame(root)
dropdown_frame.place(x=1058, y=0)
# Create an entry widget to display the selected options
dropdown_entry_var = tk.StringVar()
dropdown_entry_var.set("Select options...")
dropdown_entry = tk.Entry(dropdown_frame, textvariable=dropdown_entry_var, width=19, font=('Times', 26))
dropdown_entry.pack()

# Create a listbox widget to display the options when the dropdown is opened
dropdown_visible = False
listbox = tk.Listbox(dropdown_frame, selectmode=tk.MULTIPLE, font=('Times', 18))
for option in additional_info:
    listbox.insert(tk.END, option)
listbox.pack_forget()

# Bind events to the entry and listbox widgets to handle the dropdown behavior
dropdown_entry.bind("<Button-1>", toggle_dropdown)
listbox.bind("<FocusOut>", lambda event: dropdown_entry.focus())
listbox.bind("<Button-1>", lambda event: dropdown_entry.focus())
listbox.bind("<ButtonRelease-1>", lambda event: update_selection)

add_info_go_button = tk.Button(root, text='GO', command=update_selection, height=2, width=5)
add_info_go_button.place(x='1404', y=3)

quit_button = tk.Button(root, text='Quit', command=root.quit, height=2, width=5)
quit_button.place(x=1480, y=0)

# Graph button
graph_button = tk.Button(root, text='Graph', command=lambda: display_stock_graph(), height=2, width=5)
graph_button.place(x=1, y=348)

root.mainloop()

