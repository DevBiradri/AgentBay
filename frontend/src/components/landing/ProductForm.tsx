import React, { useState, ChangeEvent, FormEvent } from 'react';
import { Save, Edit3, Upload } from 'lucide-react';

export type ProductData = {
  imageFile: File | null;
  title: string;
  description: string;
  category: string;
  tags: string;
  price: string;
};

type ProductFormProps = {
  initialData?: ProductData;
  onSubmit: (data: ProductData) => void;
};

const ProductForm: React.FC<ProductFormProps> = ({
  initialData = { imageFile: null, title: '', description: '', category: '', tags: '', price: '' },
  onSubmit,
}) => {
  const [productData, setProductData] = useState<ProductData>(initialData);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setProductData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setProductData((prev) => ({ ...prev, imageFile: file }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(productData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File upload */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Product Image
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4
                     file:rounded-lg file:border-0
                     file:text-sm file:font-semibold
                     file:bg-purple-50 file:text-purple-700
                     hover:file:bg-purple-100"
        />
        {productData.imageFile && (
          <p className="mt-2 text-sm text-slate-600">{productData.imageFile.name}</p>
        )}
      </div>

      {/* Rest of the fields */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Product Title
          </label>
          <input
            type="text"
            name="title"
            value={productData.title}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Enter product title"
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Category
          </label>
          <select
            name="category"
            value={productData.category}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select category</option>
            <option value="Electronics">Electronics</option>
            <option value="Fashion">Fashion</option>
            <option value="Home & Garden">Home & Garden</option>
            <option value="Sports">Sports & Outdoors</option>
          </select>
        </div>

        {/* Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={productData.description}
            onChange={handleChange}
            rows={4}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Describe your product"
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Tags (comma separated)
          </label>
          <input
            type="text"
            name="tags"
            value={productData.tags}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="wireless, premium, electronics"
          />
        </div>

        {/* Price */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Price ($)
          </label>
          <input
            type="number"
            name="price"
            value={productData.price}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="0.00"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex space-x-4">
        <button
          type="submit"
          className="flex items-center px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all"
        >
          <Save className="w-4 h-4 mr-2" />
          Publish Listing
        </button>
        <button
          type="button"
          onClick={() => onSubmit(productData)}
          className="flex items-center px-6 py-3 border border-slate-300 text-slate-700 font-semibold rounded-lg hover:bg-slate-50 transition-colors"
        >
          <Edit3 className="w-4 h-4 mr-2" />
          Save as Draft
        </button>
      </div>
    </form>
  );
};

export default ProductForm;
