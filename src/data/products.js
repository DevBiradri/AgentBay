// src/data/products.js

const categories = [
  { name: 'Electronics', count: 1234, color: 'from-blue-500 to-cyan-500' },
  { name: 'Fashion', count: 856, color: 'from-pink-500 to-purple-500' },
  { name: 'Home & Garden', count: 642, color: 'from-green-500 to-teal-500' },
  { name: 'Sports', count: 423, color: 'from-orange-500 to-red-500' },
  { name: 'Books', count: 789, color: 'from-indigo-500 to-purple-500' },
  { name: 'Toys', count: 234, color: 'from-yellow-500 to-orange-500' },
];

const products = [
  {
    id: 1,
    title: 'Premium Wireless Headphones',
    price: 199.99,
    originalPrice: 249.99,
    rating: 4.8,
    reviews: 127,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop',
    category: 'Electronics',
    isWishlisted: false
  },
  {
    id: 2,
    title: 'Vintage Leather Jacket',
    price: 89.99,
    originalPrice: 120.00,
    rating: 4.6,
    reviews: 89,
    image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop',
    category: 'Fashion',
    isWishlisted: true
  },
  {
    id: 3,
    title: 'Smart Home Assistant',
    price: 79.99,
    originalPrice: 99.99,
    rating: 4.7,
    reviews: 203,
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop',
    category: 'Electronics',
    isWishlisted: false
  },
  {
    id: 4,
    title: 'Organic Cotton T-Shirt',
    price: 24.99,
    originalPrice: 34.99,
    rating: 4.5,
    reviews: 156,
    image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop',
    category: 'Fashion',
    isWishlisted: false
  },
  {
    id: 5,
    title: 'Ceramic Plant Pot Set',
    price: 39.99,
    originalPrice: 55.99,
    rating: 4.9,
    reviews: 78,
    image: 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=300&h=300&fit=crop',
    category: 'Home & Garden',
    isWishlisted: true
  },
  {
    id: 6,
    title: 'Yoga Mat Premium',
    price: 49.99,
    originalPrice: 69.99,
    rating: 4.8,
    reviews: 245,
    image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=300&h=300&fit=crop',
    category: 'Sports',
    isWishlisted: false
  }
];

export { products, categories };
