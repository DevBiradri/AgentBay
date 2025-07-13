import { useEffect, useState } from "react";
import axios from "axios";
import RecommendationCards from "@/components/RecommendationCards";

type Recommendation = {
  id?: number;
  title: string;
  description: string;
  category: string;
  brand?: string;
  model?: string;
  current_bid?: number | null;
  suggested_price: number;
  tags: string[];
  image_url?: string;
};

const Products = () => {
  const [products, setProducts] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/products")
      .then((response) => {
        console.log("API Response:", response.data);
        setProducts(response.data || []);
      })
      .catch((error) => {
        console.error("Error fetching products:", error);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-8">
      <h1 className="text-3xl font-bold mb-6">All Products</h1>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <RecommendationCards recommendations={products} handleBidClick={() => {}} useCarousel={false} />
      )}
    </div>
  );
};

export default Products;