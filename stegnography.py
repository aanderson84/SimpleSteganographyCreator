import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import numpy as np
from PIL import Image, ImageTk  # For loading, resizing, and displaying images

def encode_text_in_image(image_path, secret_text, output_path):
    """
    Encode secret text into an image using LSB steganography.
    Supports input in any common format (PNG, JPG, JPEG, BMP, etc.) and saves output as PNG for lossless preservation.
    """
    try:
        # Load the image using PIL for broad format support
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')  # Ensure RGB for 3 channels
        
        # Convert to numpy array (H x W x 3)
        image_array = np.array(image, dtype=np.uint8)
        
        # Flatten the image for easier bit manipulation
        flat_image = image_array.flatten()
        
        # Convert secret text to binary string
        binary_secret = ''.join(format(ord(char), '08b') for char in secret_text)
        binary_secret += '00000000'  # Null terminator to mark end
        
        if len(binary_secret) > len(flat_image):
            raise ValueError("Secret too long for image capacity!")
        
        # Embed bits into LSBs
        for i, bit in enumerate(binary_secret):
            flat_image[i] = (flat_image[i] & 0xFE) | int(bit)  # Clear LSB and set new bit
        
        # Reshape back to original shape
        stego_array = flat_image.reshape(image_array.shape)
        
        # Convert back to PIL Image and save as PNG
        stego_image = Image.fromarray(stego_array, mode='RGB')
        stego_image.save(output_path, format='PNG')
        
        return True, f"Encoded image saved to {output_path}"
    except Exception as e:
        return False, str(e)

def decode_text_from_image(image_path):
    """
    Decode secret text from an image using LSB steganography.
    Supports any common format for input.
    """
    try:
        # Load the image using PIL for broad format support
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.uint8)
        
        # Flatten and extract LSBs
        flat_image = image_array.flatten()
        binary_data = ''
        for pixel in flat_image:
            binary_data += str(pixel & 1)  # Get LSB
        
        # Convert binary to text chunks (8 bits each)
        text = ''
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if byte == '00000000':  # Null terminator
                break
            text += chr(int(byte, 2))
        
        return True, text
    except Exception as e:
        return False, str(e)

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Steganography Tool")
        self.root.geometry("800x600")  # Adjusted for better side-by-side layout
        
        # Variables
        self.input_image_path = tk.StringVar()
        self.output_image_path = tk.StringVar()
        self.secret_text = tk.StringVar()
        self.extracted_text = tk.StringVar()
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Image Steganography", font=("Arial", 16))
        title.pack(pady=10)
        
        # Notebook for tabs (Encode/Decode)
        from tkinter import ttk
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Encode Tab
        encode_frame = ttk.Frame(notebook)
        notebook.add(encode_frame, text="Encode")
        self.create_encode_tab(encode_frame)
        
        # Decode Tab
        decode_frame = ttk.Frame(notebook)
        notebook.add(decode_frame, text="Decode")
        self.create_decode_tab(decode_frame)
    
    def create_encode_tab(self, parent):
        # Configure grid columns: left for controls (expand), right for preview (fixed)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.rowconfigure(6, weight=1)  # For any expansion if needed
        
        # Input Image section (rows 0-2, col 0)
        tk.Label(parent, text="Input Image (any format):", anchor='w').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.Entry(parent, textvariable=self.input_image_path, width=40).grid(row=1, column=0, sticky='ew', padx=5, pady=2)
        tk.Button(parent, text="Browse", command=self.browse_input_image).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        
        # Preview in right column (spans rows 0-2 for alignment)
        self.preview_label_encode = tk.Label(parent, text="Preview (will appear after browsing)")
        self.preview_label_encode.grid(row=0, column=1, rowspan=3, padx=10, pady=2, sticky='nsew')
        
        # Secret Text section (rows 3-4, col 0)
        tk.Label(parent, text="Secret Text:", anchor='w').grid(row=3, column=0, sticky='w', padx=5, pady=(10,0))
        tk.Entry(parent, textvariable=self.secret_text, width=40, show="*").grid(row=4, column=0, sticky='ew', padx=5, pady=2)
        tk.Button(parent, text="From File", command=self.load_text_from_file).grid(row=5, column=0, sticky='w', padx=5, pady=2)
        
        # Output Image section (rows 6-7, col 0)
        tk.Label(parent, text="Output Image (saved as PNG):", anchor='w').grid(row=6, column=0, sticky='w', padx=5, pady=(10,0))
        tk.Entry(parent, textvariable=self.output_image_path, width=40).grid(row=7, column=0, sticky='ew', padx=5, pady=2)
        tk.Button(parent, text="Browse", command=self.browse_output_image).grid(row=8, column=0, sticky='w', padx=5, pady=2)
        
        # Note (row 9, col 0)
        note = tk.Label(parent, text="Note: Input images are converted to RGB if needed; output is always PNG for lossless stego.", fg='gray', anchor='w', justify='left')
        note.grid(row=9, column=0, sticky='w', padx=5, pady=5)
        
        # Encode Button fixed at bottom (row 10, col 0)
        self.encode_button = tk.Button(parent, text="Encode", command=self.encode, bg='lightgreen')
        self.encode_button.grid(row=10, column=0, pady=20, padx=5, sticky='w')
    
    def create_decode_tab(self, parent):
        # Configure grid columns: left for controls (expand), right for preview (fixed)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.rowconfigure(4, weight=1)  # For text area expansion
        
        # Input Image section (rows 0-2, col 0)
        tk.Label(parent, text="Stego Image (any format):", anchor='w').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.Entry(parent, textvariable=self.input_image_path, width=40).grid(row=1, column=0, sticky='ew', padx=5, pady=2)
        tk.Button(parent, text="Browse", command=self.browse_input_image).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        
        # Preview in right column (spans rows 0-2 for alignment)
        self.preview_label_decode = tk.Label(parent, text="Preview (will appear after browsing)")
        self.preview_label_decode.grid(row=0, column=1, rowspan=3, padx=10, pady=2, sticky='nsew')
        
        # Decode Button fixed below input (row 3, col 0)
        self.decode_button = tk.Button(parent, text="Decode", command=self.decode, bg='lightblue')
        self.decode_button.grid(row=3, column=0, pady=20, padx=5, sticky='w')
        
        # Extracted Text (row 4, col 0, spans columns for width)
        tk.Label(parent, text="Extracted Text:", anchor='w').grid(row=4, column=0, sticky='w', padx=5, pady=(10,0))
        self.text_display = scrolledtext.ScrolledText(parent, width=50, height=10)
        self.text_display.grid(row=5, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
    
    def browse_input_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp")])
        if filename:
            self.input_image_path.set(filename)
            self.update_preview()
    
    def update_preview(self):
        path = self.input_image_path.get()
        if path:
            try:
                img = Image.open(path)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)  # Resize to fit within 200x200
                photo = ImageTk.PhotoImage(img)
                
                # Update encode preview
                self.preview_label_encode.config(image=photo, text="")
                self.preview_label_encode.image = photo  # Keep a reference
                
                # Update decode preview (same image)
                self.preview_label_decode.config(image=photo, text="")
                self.preview_label_decode.image = photo  # Keep a reference
                
            except Exception as e:
                self.preview_label_encode.config(image='', text="Preview failed to load")
                self.preview_label_decode.config(image='', text="Preview failed to load")
    
    def browse_output_image(self):
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if filename:
            self.output_image_path.set(filename)
    
    def load_text_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'r') as f:
                self.secret_text.set(f.read())
    
    def encode(self):
        if not all([self.input_image_path.get(), self.secret_text.get(), self.output_image_path.get()]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        success, msg = encode_text_in_image(self.input_image_path.get(), self.secret_text.get(), self.output_image_path.get())
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
    
    def decode(self):
        if not self.input_image_path.get():
            messagebox.showerror("Error", "Please select an image!")
            return
        
        success, text = decode_text_from_image(self.input_image_path.get())
        if success:
            self.extracted_text.set(text)
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, text)
        else:
            messagebox.showerror("Error", text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.mainloop()