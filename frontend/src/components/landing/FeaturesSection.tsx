import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Camera, Shield, Mic, CheckCircle } from "lucide-react";
import uploadFeature from "@/assets/upload-feature.jpg";
import searchFeature from "@/assets/search-feature.jpg";

const FeaturesSection = () => {
  return (
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
  );
};

export default FeaturesSection;