import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk  # For displaying images in Tkinter

def encode_text_in_image(image_path, secret_text, output_path):
    """
    Encode secret text into an image using LSB steganography.
    """
    try:
        # Read the image as a numpy array (H x W x 3 for RGB)
        image = plt.imread(image_path)
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        # Flatten the image for easier bit manipulation
        flat_image = image.flatten()
        
        # Convert secret text to binary string
        binary_secret = ''.join(format(ord(char), '08b') for char in secret_text)
        binary_secret += '00000000'  # Null terminator to mark end
        
        if len(binary_secret) > len(flat_image):
            raise ValueError("Secret too long for image capacity!")
        
        # Embed bits into LSBs
        for i, bit in enumerate(binary_secret):
            flat_image[i] = (flat_image[i] & 0xFE) | int(bit)  # Clear LSB and set new bit
        
        # Reshape back to original shape
        stego_image = flat_image.reshape(image.shape)
        
        # Save the stego image
        plt.imsave(output_path, stego_image, format='PNG')
        return True, f"Encoded image saved to {output_path}"
    except Exception as e:
        return False, str(e)

def decode_text_from_image(image_path):
    """
    Decode secret text from an image using LSB steganography.
    """
    try:
        # Read the image
        image = plt.imread(image_path)
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        # Flatten and extract LSBs
        flat_image = image.flatten()
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
        self.root.geometry("600x500")
        
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
        # Input Image
        tk.Label(parent, text="Input Image:").pack(anchor='w')
        tk.Entry(parent, textvariable=self.input_image_path, width=50).pack(anchor='w')
        tk.Button(parent, text="Browse", command=self.browse_input_image).pack(anchor='w', pady=2)
        
        # Secret Text
        tk.Label(parent, text="Secret Text:").pack(anchor='w', pady=(10,0))
        tk.Entry(parent, textvariable=self.secret_text, width=50, show="*").pack(anchor='w')
        tk.Button(parent, text="From File", command=self.load_text_from_file).pack(anchor='w', pady=2)
        
        # Output Image
        tk.Label(parent, text="Output Image:").pack(anchor='w', pady=(10,0))
        tk.Entry(parent, textvariable=self.output_image_path, width=50).pack(anchor='w')
        tk.Button(parent, text="Browse", command=self.browse_output_image).pack(anchor='w', pady=2)
        
        # Encode Button
        tk.Button(parent, text="Encode", command=self.encode, bg='lightgreen').pack(pady=20)
    
    def create_decode_tab(self, parent):
        # Input Image
        tk.Label(parent, text="Stego Image:").pack(anchor='w')
        tk.Entry(parent, textvariable=self.input_image_path, width=50).pack(anchor='w')
        tk.Button(parent, text="Browse", command=self.browse_input_image).pack(anchor='w', pady=2)
        
        # Decode Button
        tk.Button(parent, text="Decode", command=self.decode, bg='lightblue').pack(pady=20)
        
        # Extracted Text
        tk.Label(parent, text="Extracted Text:").pack(anchor='w', pady=(10,0))
        self.text_display = scrolledtext.ScrolledText(parent, width=60, height=10)
        self.text_display.pack(pady=5, fill='both', expand=True)
    
    def browse_input_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.input_image_path.set(filename)
    
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