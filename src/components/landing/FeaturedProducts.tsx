import React from 'react';
import { Heart, Star, ShoppingCart } from 'lucide-react';

type Product = {
  id: number;
  title: string;
  price: number;
  originalPrice: number;
  rating: number;
  reviews: number;
  image: string;
  category: string;
  isWishlisted: boolean;
};

type Props = {
  products: Product[];
  viewMode?: 'grid' | 'list';
};

const FeaturedProducts: React.FC<Props> = ({ products, viewMode = 'grid' }) => {
  return (
    <div className="mb-5 p-5">
      <div className="flex justify-center gap-20 items-center mb-6">
        <h2 className="text-xl  font-semibold text-slate-900">Featured Products</h2>
        <button className="text-blue-500 hover:text-blue-600 font-medium">View all</button>
      </div>

      <div className={`grid ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'} gap-6`}>
        {products.map((product) => (
          <div key={product.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow overflow-hidden group">
            <div className="relative">
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <button className={`absolute top-3 right-3 p-2 rounded-full ${product.isWishlisted ? 'bg-red-500 text-white' : 'bg-white text-slate-400'} hover:scale-110 transition-transform`}>
                <Heart className="w-4 h-4" fill={product.isWishlisted ? 'currentColor' : 'none'} />
              </button>
              <div className="absolute top-3 left-3 px-2 py-1 bg-blue-500 text-white text-xs font-semibold rounded-full">
                {Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)}% OFF
              </div>
            </div>

            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-blue-500 font-medium">{product.category}</span>
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="text-sm text-slate-600 ml-1">{product.rating} ({product.reviews})</span>
                </div>
              </div>

              <h3 className="font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                {product.title}
              </h3>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold text-slate-900">${product.price}</span>
                  <span className="text-sm text-slate-500 line-through">${product.originalPrice}</span>
                </div>
                <button className="flex items-center px-3 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all">
                  <ShoppingCart className="w-4 h-4 mr-1" />
                  Add
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeaturedProducts;
