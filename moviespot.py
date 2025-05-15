import json
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from random import randint
from datetime import datetime

# Function to initialize movie data and bookings
def initialize_data():
    global movies, bookings
    
    movies = [
        {
            "title": "Inception",
            "available_seats": [np.full((13, 10), True) for _ in range(5)],
            "show_times": ("10:00 AM", "01:00 PM", "04:00 PM", "07:00 PM", "10:00 PM")
        },
        {
            "title": "The Matrix",
            "available_seats": [np.full((13, 10), True) for _ in range(5)],
            "show_times": ("09:00 AM", "12:00 PM", "03:00 PM", "06:00 PM", "09:00 PM")
        },
        {
            "title": "Interstellar",
            "available_seats": [np.full((13, 10), True) for _ in range(5)],
            "show_times": ("11:00 AM", "02:00 PM", "05:00 PM", "08:00 PM", "11:00 PM")
        },
    ]

    bookings = []

def load_data(filename):
    global movies, bookings
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            movies = []
            for movie_data in data["movies"]:
                movies.append({
                    "title": movie_data["title"],
                    "available_seats": [np.array(show) for show in movie_data["available_seats"]],
                    "show_times": tuple(movie_data["show_times"])
                })
            bookings = data["bookings"]
    except FileNotFoundError:
        initialize_data()

def save_data(filename):
    data = {
        "movies": [{
            "title": movie["title"],
            "available_seats": [seats.tolist() for seats in movie["available_seats"]],
            "show_times": movie["show_times"]
        } for movie in movies],
        "bookings": bookings
    }
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

class SeatSelection:
    def __init__(self, parent, movie_idx, showtime_idx):
        self.parent = parent
        self.movie = movies[movie_idx]
        self.showtime_idx = showtime_idx
        self.seats = self.movie["available_seats"][showtime_idx]
        self.selected_seats = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Select Seats")
        
        # Screen display
        screen_frame = tk.Frame(self.window, bg='gray', height=40)
        screen_frame.pack(fill='x', pady=10)
        tk.Label(screen_frame, text="S C R E E N", font=('Arial', 14, 'bold'), 
                bg='gray', fg='white').pack(pady=5)
        
        # Seat grid
        grid_frame = tk.Frame(self.window)
        grid_frame.pack(padx=20, pady=10)
        
        # Create seat buttons
        self.buttons = []
        for row in range(13):
            row_label = tk.Label(grid_frame, text=chr(65 + row))
            row_label.grid(row=row+1, column=0, padx=5)
            for col in range(10):
                btn = tk.Button(grid_frame, text=f"{col+1}", width=3,
                               command=lambda r=row, c=col: self.toggle_seat(r, c))
                btn.grid(row=row+1, column=col+1, padx=2, pady=2)
                if not self.seats[row][col]:
                    btn.config(state=tk.DISABLED, bg='#ff9999')
                self.buttons.append(btn)
        
        # Exit doors
        tk.Label(grid_frame, text="EXIT", font=('Arial', 8)).grid(row=0, column=0, columnspan=11)
        tk.Label(grid_frame, text="EXIT", font=('Arial', 8)).grid(row=14, column=0, columnspan=11)
        
        # Controls
        control_frame = tk.Frame(self.window)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Confirm Seats", command=self.confirm).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def toggle_seat(self, row, col):
        seat_id = f"{chr(65 + row)}{col+1}"
        btn = self.buttons[row * 10 + col]
        
        if seat_id in self.selected_seats:
            self.selected_seats.remove(seat_id)
            btn.config(bg='SystemButtonFace' if self.seats[row][col] else '#ff9999')
        else:
            if len(self.selected_seats) >= 10:
                messagebox.showwarning("Limit Exceeded", "Max 10 seats per booking")
                return
            self.selected_seats.append(seat_id)
            btn.config(bg='#99ff99')
    
    def confirm(self):
        if not self.selected_seats:
            messagebox.showwarning("No Seats", "Please select at least one seat")
            return
        self.window.destroy()
        PaymentWindow(self.parent, self.movie, self.showtime_idx, self.selected_seats)

class PaymentWindow:
    def __init__(self, parent, movie, showtime_idx, seats):
        self.parent = parent
        self.movie = movie
        self.showtime_idx = showtime_idx
        self.seats = seats
        
        self.window = tk.Toplevel(parent)
        self.window.title("Payment")
        
        tk.Label(self.window, text="Payment Details", font=('Arial', 14)).pack(pady=10)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(padx=20, pady=10)
        
        tk.Label(form_frame, text="Card Number:").grid(row=0, column=0, sticky='e')
        self.card_entry = tk.Entry(form_frame, width=20)
        self.card_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Expiry (MM/YY):").grid(row=1, column=0, sticky='e')
        self.expiry_entry = tk.Entry(form_frame, width=8)
        self.expiry_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="CVV:").grid(row=2, column=0, sticky='e')
        self.cvv_entry = tk.Entry(form_frame, width=4, show='*')
        self.cvv_entry.grid(row=2, column=1, pady=5)
        
        tk.Button(self.window, text="Process Payment", command=self.process_payment).pack(pady=10)
    
    def process_payment(self):
        card_number = self.card_entry.get().replace(" ", "")
        expiry = self.expiry_entry.get()
        cvv = self.cvv_entry.get()
        
        if not (len(card_number) == 16 and card_number.isdigit()):
            messagebox.showerror("Error", "Invalid card number")
            return
        if not (len(expiry) == 5 and expiry[2] == '/' and expiry[:2].isdigit() and expiry[3:].isdigit()):
            messagebox.showerror("Error", "Invalid expiry date")
            return
        if not (len(cvv) == 3 and cvv.isdigit()):
            messagebox.showerror("Error", "Invalid CVV")
            return
        
        self.window.destroy()
        self.generate_ticket(card_number[-4:])
    
    def generate_ticket(self, card_last4):
        total_price = len(self.seats) * 200  # ₹200 per seat
        booking_id = f"{datetime.now().strftime('%Y%m%d')}-{randint(1000,9999)}"
        
        ticket_window = tk.Toplevel(self.parent)
        ticket_window.title("Booking Confirmation")
        
        tk.Label(ticket_window, text="🎉 TICKET CONFIRMED 🎉", font=('Arial', 16, 'bold')).pack(pady=10)
        
        details = [
            f"Booking ID: {booking_id}",
            f"Movie: {self.movie['title']}",
            f"Showtime: {self.movie['show_times'][self.showtime_idx]}",
            f"Seats: {', '.join(self.seats)}",
            f"Total Paid: ₹{total_price}",
            f"Payment Method: Card ****{card_last4}",
            f"Booked At: {datetime.now().strftime('%d %b %Y %H:%M:%S')}"
        ]
        
        for line in details:
            tk.Label(ticket_window, text=line, font=('Arial', 12)).pack(pady=2)
        
        # Update movie seats
        for seat in self.seats:
            row = ord(seat[0].upper()) - ord('A')
            col = int(seat[1:]) - 1
            self.movie["available_seats"][self.showtime_idx][row][col] = False
        
        # Save booking
        bookings.append({
            "booking_id": booking_id,
            "movie": self.movie["title"],
            "showtime": self.movie["show_times"][self.showtime_idx],
            "seats": self.seats,
            "total": total_price,
            "payment_last4": card_last4,
            "timestamp": datetime.now().isoformat()
        })
        
        tk.Button(ticket_window, text="Save Ticket", 
                 command=lambda: self.save_ticket(details)).pack(pady=10)
    
    def save_ticket(self, details):
        filename = f"ticket_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write("\n".join(details))
        messagebox.showinfo("Saved", f"Ticket saved as {filename}")

def book_ticket():
    display_movies()
    movie_idx = simpledialog.askinteger("Movie", "Enter movie number:", parent=root, minvalue=1, maxvalue=len(movies))
    if not movie_idx: return
    movie_idx -= 1
    
    showtimes = movies[movie_idx]["show_times"]
    showtime_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(showtimes)])
    showtime_idx = simpledialog.askinteger("Showtime", f"Available showtimes:\n{showtime_str}", 
                                        parent=root, minvalue=1, maxvalue=len(showtimes))
    if not showtime_idx: return
    showtime_idx -= 1
    
    SeatSelection(root, movie_idx, showtime_idx)

def display_movies():
    movies_info = "Current Movies:\n\n"
    for i, movie in enumerate(movies, 1):
        movies_info += f"{i}. {movie['title']}\n"
        movies_info += f"   Showtimes: {', '.join(movie['show_times'])}\n\n"
    messagebox.showinfo("Now Showing", movies_info)

def display_bookings():
    if not bookings:
        messagebox.showinfo("Bookings", "No bookings yet")
        return
    
    bookings_window = tk.Toplevel(root)
    bookings_window.title("Booking History")
    
    tree = ttk.Treeview(bookings_window, columns=('ID', 'Movie', 'Showtime', 'Seats', 'Amount'), show='headings')
    tree.heading('ID', text='Booking ID')
    tree.heading('Movie', text='Movie')
    tree.heading('Showtime', text='Showtime')
    tree.heading('Seats', text='Seats')
    tree.heading('Amount', text='Amount')
    
    for booking in bookings:
        tree.insert('', 'end', values=(
            booking['booking_id'],
            booking['movie'],
            booking['showtime'],
            ', '.join(booking['seats']),
            f"₹{booking['total']}"
        ))
    
    tree.pack(fill='both', expand=True)

def main():
    global root
    root = tk.Tk()
    root.title("CineBook Pro")
    root.geometry("600x400")
    
    header = tk.Frame(root, bg='#2c3e50', height=80)
    header.pack(fill='x')
    tk.Label(header, text="CINEPLEX", font=('Arial', 24, 'bold'), 
            bg='#2c3e50', fg='white').pack(pady=20)
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)
    
    tk.Button(btn_frame, text="Book Tickets", command=book_ticket, 
             width=15, height=2).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="View Bookings", command=display_bookings,
             width=15, height=2).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Exit", command=lambda: [save_data('bookings.json'), root.quit()],
             width=15, height=2).grid(row=0, column=2, padx=10)
    
    load_data('bookings.json')
    root.mainloop()

if __name__ == "__main__":
    main()