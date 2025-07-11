import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Camera, Search, Shield, Sparkles, Upload, Mic, CheckCircle } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import marketplaceHero from "@/assets/marketplace-hero.jpg";
import uploadFeature from "@/assets/upload-feature.jpg";
import searchFeature from "@/assets/search-feature.jpg";

const Index = () => {
  const [userRole, setUserRole] = useState<'buyer' | 'seller' | null>(null);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container flex h-16 items-center">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              AIMarket
            </span>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="ghost">Sign In</Button>
            <Button variant="hero" onClick={() => navigate('/chat')}>Get Started</Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-24 md:py-32">
        <div className="absolute inset-0 bg-gradient-hero opacity-90" />
        <div className="absolute inset-0">
          <img 
            src={marketplaceHero} 
            alt="AI Marketplace Hero" 
            className="w-full h-full object-cover mix-blend-overlay"
          />
        </div>
        <div className="relative container max-w-5xl text-center">
          <Badge className="mb-6 bg-primary/10 text-primary border-primary/20" variant="outline">
            <Sparkles className="w-3 h-3 mr-1" />
            AI-Powered Marketplace
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-slide-up">
            Buy & Sell with
            <span className="bg-gradient-to-r from-blue-200 to-green-200 bg-clip-text text-transparent block">
              AI Intelligence
            </span>
          </h1>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto animate-slide-up">
            Upload photos, get AI descriptions, and discover products with voice search. 
            Experience the future of online marketplace today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up">
            <Button 
              size="lg" 
              variant="hero"
              onClick={() => navigate('/chat')}
              className="text-lg"
            >
              <Upload className="w-5 h-5 mr-2" />
              Start Selling
            </Button>
            <Button 
              size="lg" 
              variant="marketplace"
              onClick={() => navigate('/chat')}
              className="text-lg"
            >
              <Search className="w-5 h-5 mr-2" />
              Shop Now
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-muted/30">
        <div className="container max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powered by Advanced AI
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our intelligent platform makes buying and selling effortless with cutting-edge AI technology
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="relative overflow-hidden shadow-card hover:shadow-product transition-all duration-300 group">
              <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-opacity duration-300" />
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-primary rounded-lg flex items-center justify-center mb-4">
                  <Camera className="w-8 h-8 text-white" />
                </div>
                <CardTitle>Smart Photo Upload</CardTitle>
                <CardDescription>
                  Upload product photos and let AI create perfect descriptions automatically
                </CardDescription>
              </CardHeader>
              <CardContent>
                <img 
                  src={uploadFeature} 
                  alt="Upload Feature" 
                  className="w-full h-48 object-cover rounded-lg"
                />
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden shadow-card hover:shadow-product transition-all duration-300 group">
              <div className="absolute inset-0 bg-gradient-secondary opacity-0 group-hover:opacity-5 transition-opacity duration-300" />
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-secondary rounded-lg flex items-center justify-center mb-4">
                  <Mic className="w-8 h-8 text-white" />
                </div>
                <CardTitle>Voice & Text Search</CardTitle>
                <CardDescription>
                  Find products using voice commands or text with AI-powered search suggestions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <img 
                  src={searchFeature} 
                  alt="Search Feature" 
                  className="w-full h-48 object-cover rounded-lg"
                />
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden shadow-card hover:shadow-product transition-all duration-300 group">
              <div className="absolute inset-0 bg-gradient-to-br from-warning/10 to-success/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-br from-warning to-success rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <CardTitle>Scam Detection</CardTitle>
                <CardDescription>
                  Advanced AI algorithms detect and prevent potential scams, keeping you safe
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2 text-success">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">99.9% Protection Rate</span>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <CheckCircle className="w-4 h-4 mr-2 text-success" />
                    Real-time verification
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <CheckCircle className="w-4 h-4 mr-2 text-success" />
                    AI risk assessment
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <CheckCircle className="w-4 h-4 mr-2 text-success" />
                    Secure transactions
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24">
        <div className="container max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-16">
            How It Works
          </h2>
          <div className="grid md:grid-cols-2 gap-12">
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-primary">For Sellers</h3>
              <div className="space-y-4 text-left">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-bold text-sm">1</div>
                  <div>
                    <h4 className="font-semibold">Upload Photos</h4>
                    <p className="text-muted-foreground">Take or upload photos of your items</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-bold text-sm">2</div>
                  <div>
                    <h4 className="font-semibold">AI Description</h4>
                    <p className="text-muted-foreground">Our AI creates compelling product descriptions</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-bold text-sm">3</div>
                  <div>
                    <h4 className="font-semibold">Review & Publish</h4>
                    <p className="text-muted-foreground">Review, edit if needed, and publish your listing</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-secondary">For Buyers</h3>
              <div className="space-y-4 text-left">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-white font-bold text-sm">1</div>
                  <div>
                    <h4 className="font-semibold">Search Products</h4>
                    <p className="text-muted-foreground">Use voice or text to find what you need</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-white font-bold text-sm">2</div>
                  <div>
                    <h4 className="font-semibold">AI Suggestions</h4>
                    <p className="text-muted-foreground">Get personalized recommendations</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-white font-bold text-sm">3</div>
                  <div>
                    <h4 className="font-semibold">Safe Purchase</h4>
                    <p className="text-muted-foreground">Buy with confidence using AI scam protection</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-hero relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20" />
        <div className="relative container max-w-3xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Marketplace Experience?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of users already enjoying smarter buying and selling
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="hero" className="text-lg" onClick={() => navigate('/chat')}>
              Start Selling Today
            </Button>
            <Button size="lg" variant="marketplace" className="text-lg" onClick={() => navigate('/chat')}>
              Browse Products
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 bg-muted/30">
        <div className="container max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">AIMarket</span>
            </div>
            <p className="text-muted-foreground">
              © 2024 AIMarket. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
