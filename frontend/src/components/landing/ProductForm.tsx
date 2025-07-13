import React, { useState, ChangeEvent, FormEvent } from 'react';
import { Save, Edit3, Upload } from 'lucide-react';
import axios from 'axios';
import Swal from 'sweetalert2';

export type ProductData = {
  imageFile: File | null;
  title: string;
  description: string;
  category: string;
  tags: string;
  price: string;
  imageUrl?: string;
  condition?: string;
  brand?: string;
  model?: string;
  confidence_score?: number;
};

type ProductFormProps = {
  initialData?: ProductData;
  onSubmit: (data: ProductData) => void;
  onImageUpload?: (file: File) => void;
  imagePreview?: string;
  imageLoading?: boolean;
  submitButtonColor?: string;
  imageUrl?: string;
  condition?: string;
  brand?: string;
  model?: string;
  confidence_score?: number;
};

const ProductForm: React.FC<ProductFormProps> = ({
  initialData = { imageFile: null, title: '', description: '', category: '', tags: '', price: '' },
  onSubmit,
  onImageUpload,
  imagePreview,
  imageLoading,
  submitButtonColor,
  imageUrl,
  condition,
  brand,
  model,
  confidence_score,
}) => {
  const [productData, setProductData] = useState<ProductData>(initialData);

  // Update form fields when initialData changes
  React.useEffect(() => {
    setProductData(initialData);
  }, [initialData]);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setProductData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setProductData((prev) => ({ ...prev, imageFile: file }));
    if (file && onImageUpload) {
      onImageUpload(file);
    }
  };


  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      let data = JSON.stringify({
        title: productData.title,
        description: productData.description,
        condition: condition || "new",
        category: productData.category,
        suggested_price: Number(productData.price),
        current_bid: null,
        tags: productData.tags.split(',').map(tag => tag.trim()),
        brand: brand || "",
        model: model || "",
        confidence_score: confidence_score !== undefined ? confidence_score : 0.95,
        image_url: imageUrl || "",
      });
      let config = {
        method: 'post',
        maxBodyLength: Infinity,
        url: 'http://localhost:8000/api/products',
        headers: { 'Content-Type': 'application/json' },
        data: data
      };
      await axios.request(config);
      Swal.fire({
        title: 'Success!',
        customClass: {
          popup: 'swal-glass'
        },
        text: 'Listing created successfully.',
        icon: 'success',
        confirmButtonColor: '#10b981'
      });
      setProductData({
        imageFile: null,
        title: '',
        description: '',
        category: '',
        tags: '',
        price: '',
      });
    } catch (error) {
      console.log("Error creating listing:", error);
      Swal.fire({
        title: 'Error!',
        customClass: {
          popup: 'swal-glass'
        },
        text: 'Failed to create listing.',
        icon: 'error',
        confirmButtonColor: '#ef4444'
      });
    }
  };

  return (
    <div  className="p-8 rounded-xl shadow-xl bg-white dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
       <form onSubmit={handleSubmit} className="space-y-6">
      {/* File upload */}
      <div>
        <label className="block text-base font-semibold text-foreground mb-2">
          Product Image
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden" // Hide the default input
          id="image-upload-input"
        />
        <label
          htmlFor="image-upload-input"
          className={`flex items-center justify-center px-6 py-3 font-semibold rounded-lg transition-all cursor-pointer
            ${imageLoading ? "bg-gray-400 text-white" : "bg-gradient-to-r from-primary to-primary/90 text-white !important hover:from-primary/90 hover:to-primary"}
            `}
          style={{ fontSize: "1.15rem", height: "48px" }}
        >
          {imageLoading ? (
            <>
              <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              Uploading and analyzing...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2 dark:text-black" />
              <span className='dark:text-black'>Choose Image</span>
            </>
          )}
        </label>
        {productData.imageFile && (
          <img
            src={imagePreview}
            alt="Preview"
            className="mt-4 rounded-lg border border-primary w-full max-w-xs h-auto"
            style={{ maxHeight: "220px", objectFit: "contain", background: "#fff" }}
          />
        )}
        {productData.imageFile && (
          <p className="mt-2 text-sm text-muted-foreground">
            {productData.imageFile.name}
          </p>
        )}
      </div>

      {/* Fields */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Product Title
          </label>
          <input
            type="text"
            name="title"
            value={productData.title}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Enter product title"
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Category
          </label>
          <input
            type="text"
            name="category"
            value={productData.category}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Enter category title"
          />

        </div>

        {/* Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={productData.description}
            onChange={handleChange}
            rows={4}
            className="w-full px-4 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Describe your product"
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Tags (comma separated)
          </label>
          <input
            type="text"
            name="tags"
            value={productData.tags}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="wireless, premium, electronics"
          />
        </div>

        {/* Price */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Price ($)
          </label>
          <input
            type="number"
            name="price"
            value={productData.price}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="0.00"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex space-x-4">
        <button
          type="submit"
          className={"flex items-center px-6 py-3 text-white font-semibold rounded-lg transition-all bg-primary  hover:from-primary/90 hover:to-primary dark:text-black"}
          style={{ fontSize: "1.15rem" }}
          disabled={imageLoading}
        >
          <Save className="w-4 h-4 mr-2 dark:text-black" />
          {imageLoading ? "Processing..." : "Publish Listing"}
        </button>
        <button
          type="button"
          onClick={() =>
            setProductData({
              imageFile: null,
              title: '',
              description: '',
              category: '',
              tags: '',
              price: '',
            })}
          className="flex items-center px-6 py-3 border border-border text-foreground font-semibold rounded-lg hover:bg-accent transition-colors"
        >
          <Edit3 className="w-4 h-4 mr-2" />
          Clear
        </button>
      </div>
    </form>

    </div>
   
  );
};

export default ProductForm;
