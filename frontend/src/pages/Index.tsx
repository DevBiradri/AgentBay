import Navigation from "@/components/landing/Navigation";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";
import {products} from "@/data/products.js"
import React, { useState } from "react";
import ProductForm, { ProductData } from "@/components/landing/ProductForm";

const Index = () => {
  const [listingData, setListingData] = useState<ProductData | undefined>(undefined);

  // Handles image upload and API call
  const handleImageUpload = async (imageFile: File) => {
    const formData = new FormData();
    formData.append("image", imageFile);
    const res = await fetch("http://127.0.0.1:8000/api/agent/create-listing", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    // Map API response to ProductData
    setListingData({
      imageFile,
      title: data.product.title,
      description: data.product.description,
      category: data.product.category,
      tags: data.product.tags ? data.product.tags.join(", ") : "",
      price: data.product.suggested_price?.toString() || "",
    });
  };

  // Handles final submit to next API
  const handleSubmit = async (data: ProductData) => {
    await fetch("http://127.0.0.1:8000/api/agent/submit-listing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;