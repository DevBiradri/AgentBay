import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { Camera, Search, MessageCircle, Upload, Shield, Sparkles, Mic, ArrowLeft, Bot, Star, DollarSign, Gavel, ChevronRight, ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import axios from "axios";
import Swal from 'sweetalert2';
import RecommendationCards from "@/components/RecommendationCards";


type Mode = 'selection' | 'buyer' | 'seller';
type ChatMessage = {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
};

type Recommendation = {
  id: number;
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

const Chat = () => {
  const [mode, setMode] = useState<Mode>('selection');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recommendationHistory, setRecommendationHistory] = useState<Array<{
    query: string;
    recommendations: Recommendation[];
    timestamp: Date;
  }>>([]);
  const [bidDialogOpen, setBidDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Recommendation | null>(null);
  const [bidFormData, setBidFormData] = useState({
    user_id: '',
    amount: ''
  });
  const [isRecommendationsPanelCollapsed, setIsRecommendationsPanelCollapsed] = useState(false);
  const navigate = useNavigate();

//   speech regonigition methods
const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  useEffect(() => {
    if (transcript && isListening) {
      console.log(transcript)
      setInputText(transcript);
    }
  }, [transcript]);

  useEffect(() => {
    console.log("Listening state changed:", isListening);
  }, [isListening]);

  const toggleMic = () => {
    if (!browserSupportsSpeechRecognition) {
      alert("Speech recognition is not supported in your browser.");
      return;
    }

    if (isListening) {
      SpeechRecognition.stopListening();
      setIsListening(false);
    } else {
      resetTranscript(); // clear previous
      SpeechRecognition.startListening({ continuous: true, language: "en-US" });
      setIsListening(true);
    }
  };
//   =============================================

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentQuery = inputText;
    setInputText('');
    setIsLoading(true);

    try {
      // Call the API
      const response = await axios.post('http://127.0.0.1:8000/api/agent/recommendations', {
        query_string: currentQuery
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Set recommendations from API response and add to history
      if (response.data && response.data.results) {
        const newRecommendations = response.data.results;
        setRecommendations(newRecommendations);
        
        // Add to recommendation history
        setRecommendationHistory(prev => [...prev, {
          query: currentQuery,
          recommendations: newRecommendations,
          timestamp: new Date()
        }]);
      }

      // Add AI response message
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: mode === 'buyer'
          ? `I found ${response.data?.results?.length || 0} recommendations for "${currentQuery}". Check out the products below!`
          : "I'll help you create an optimized listing. Please upload photos of your item and I'll generate a compelling description.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('API Error:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I couldn't fetch recommendations at the moment. Please try again later.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const resetToSelection = () => {
    setMode('selection');
    setMessages([]);
    setInputText('');
    setRecommendations([]);
    setRecommendationHistory([]);
  };

  const handleBidClick = (product: Recommendation) => {
    setSelectedProduct(product);
    setBidDialogOpen(true);
  };

  const handleBidSubmit = async () => {
    if (!selectedProduct || !bidFormData.user_id || !bidFormData.amount) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/products/${selectedProduct.id}/bids`,
        {
          user_id: bidFormData.user_id,
          amount: parseFloat(bidFormData.amount)
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      await Swal.fire({
        title: 'Bid Placed Successfully!',
        text: `Your bid of $${bidFormData.amount} has been placed for ${selectedProduct.title}`,
        icon: 'success',
        confirmButtonText: 'Great!',
        confirmButtonColor: '#10b981',
        background: 'var(--background)',
        color: 'var(--foreground)',
      });
      setBidDialogOpen(false);
      setBidFormData({ user_id: '', amount: '' });
      setSelectedProduct(null);
    } catch (error) {
      console.error('Bid submission error:', error);
      await Swal.fire({
        title: 'Bid Failed',
        text: 'Failed to place bid. Please try again.',
        icon: 'error',
        confirmButtonText: 'OK',
        confirmButtonColor: '#ef4444',
        background: 'var(--background)',
        color: 'var(--foreground)',
      });
    }
  };

  if (mode === 'selection') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 relative overflow-hidden">
        {/* Futuristic background elements */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl"></div>
        
        {/* Header */}
        <nav className="relative z-10 border-b border-border/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-16 items-center">
            <Button variant="ghost" onClick={() => navigate('/')} className="mr-4 hover:bg-white/10">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center space-x-3">
              <div className="relative ">
                <Bot className="h-8 w-8 text-primary animate-pulse dark:text-primary" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full animate-ping"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                AI Assistant
              </span>
            </div>
            <div className="ml-auto">
              <ThemeToggle />
            </div>
          </div>
        </nav>

        {/* Mode Selection */}
        <div className="relative z-10 flex-1 flex items-center justify-center p-6 min-h-[calc(100vh-4rem)]">
          <div className="max-w-2xl w-full space-y-12 text-center">
            <div className="space-y-6">
              <div className="relative">
                <div className="w-24 h-24 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mx-auto shadow-glow animate-float">
                  <MessageCircle className="w-12 h-12 text-white" />
                </div>
                <div className="absolute inset-0 w-24 h-24 mx-auto rounded-full border-2 border-primary/30 animate-ping"></div>
              </div>
              <div className="space-y-3">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                  Choose Your Mission
                </h1>
                <p className="text-xl text-muted-foreground max-w-md mx-auto">
                  Let AI guide your marketplace journey
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <Card
                className="group relative overflow-hidden border-0 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl cursor-pointer transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-secondary/20"
                onClick={() => setMode('buyer')}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-secondary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <CardContent className="relative p-8 space-y-6">
                  <div className="relative">
                    <div className="w-16 h-16 bg-gradient-to-br from-secondary to-secondary/80 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <Search className="w-8 h-8 text-white" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 mx-auto rounded-2xl border border-secondary/30 animate-pulse"></div>
                  </div>
                  <div className="space-y-3">
                    <h3 className="text-2xl font-bold text-foreground">Explorer Mode</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Discover products with AI-powered search and fraud protection
                    </p>
                  </div>
                  <div className="flex justify-center">
                    <Badge variant="outline" className="border-secondary/30 text-secondary bg-secondary/5">
                      <Shield className="w-3 h-3 mr-1" />
                      Protected
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card
                className="group relative overflow-hidden border-0 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl cursor-pointer transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-primary/20"
                onClick={() => setMode('seller')}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <CardContent className="relative p-8 space-y-6">
                  <div className="relative">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <Camera className="w-8 h-8 text-white" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 mx-auto rounded-2xl border border-primary/30 animate-pulse"></div>
                  </div>
                  <div className="space-y-3">
                    <h3 className="text-2xl font-bold text-foreground">Creator Mode</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Generate perfect listings with AI descriptions and pricing
                    </p>
                  </div>
                  <div className="flex justify-center">
                    <Badge variant="outline" className="border-primary/30 text-primary bg-primary/5">
                      <Sparkles className="w-3 h-3 mr-1" />
                      AI-Powered
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card
                className="group relative overflow-hidden border-0 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl cursor-pointer transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-accent/20"
                onClick={() => navigate('/products')}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-accent/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <CardContent className="relative p-8 space-y-6">
                  <div className="relative">
                    <div className="w-16 h-16 bg-gradient-to-br from-accent to-accent/80 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <Star className="w-8 h-8 text-white" />
                    </div>
                    <div className="absolute inset-0 w-16 h-16 mx-auto rounded-2xl border border-accent/30 animate-pulse"></div>
                  </div>
                  <div className="space-y-3">
                    <h3 className="text-2xl font-bold text-foreground">View All Products</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Browse the entire marketplace catalog
                    </p>
                  </div>
                  <div className="flex justify-center">
                    <Badge variant="outline" className="border-accent/30 text-accent bg-accent/5">
                      <Star className="w-3 h-3 mr-1" />
                      All Products
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gradient-to-br relative overflow-hidden flex flex-col">
      
      {/* Futuristic background elements */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl"></div>
        
      
      {/* Header */}
      <nav className="relative z-10 border-b border-border/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60 flex-shrink-0">
        <div className="container flex h-16 items-center">
          <Button variant="ghost" onClick={resetToSelection} className="mr-4 hover:bg-white/10">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex items-center space-x-3">
            <div className="relative">
              {mode === 'buyer' ? (
                <Search className="h-6 w-6 text-secondary" />
              ) : (
                <Camera className="h-6 w-6 text-primary" />
              )}
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <span className="font-bold text-lg">
              {mode === 'buyer' ? 'Explorer Mode' : 'Creator Mode'}
            </span>
          </div>
          <div className="ml-auto">
            <Badge variant="outline" className="border-border/30 bg-background/50 backdrop-blur">
              <Bot className="w-3 h-3 mr-1" />
              {mode === 'buyer' ? 'AI Shopping Assistant' : 'AI Listing Helper'}
            </Badge>
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* Split Screen Layout or Full Screen Chat */}
      <div className="relative z-10 flex-1 flex overflow-hidden">
        {/* mic listening custom animated ui */}
        {isListening && (
          <div className="listening-overlay fixed h-[80%] mt-20 w-full flex items-center justify-center z-50">
            <div className="listening-circle">
              <Mic className="h-12 w-12 text-white" onClick={() => setIsListening(l => !l)} />
            </div>
          </div>
        )}

        {/* Left Side - Chat Messages */}
        <div className={`${messages.length > 0 && recommendationHistory.length > 0 && !isRecommendationsPanelCollapsed ? 'w-1/2 border-r border-border/20' : 'w-full'} flex flex-col transition-all duration-300`}>
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 h-full">
              <div className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'max-w-2xl' : 'max-w-4xl'} mx-auto space-y-6 transition-all duration-300`}>
              {messages.length === 0 && (
                <div className="text-center space-y-8 py-16">
                  <div className="relative">
                    <div className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'w-20 h-20' : 'w-24 h-24'} ${mode === 'buyer' ? 'bg-gradient-to-br from-secondary to-secondary/80' : 'bg-gradient-to-br from-primary to-primary/80'} rounded-full flex items-center justify-center mx-auto shadow-glow animate-float`}>
                      {mode === 'buyer' ? (
                        <Search className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'w-10 h-10' : 'w-12 h-12'} text-white`} />
                      ) : (
                        <Camera className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'w-10 h-10' : 'w-12 h-12'} text-white`} />
                      )}
                    </div>
                    <div className={`absolute inset-0 ${messages.length > 0 && recommendationHistory.length > 0 ? 'w-20 h-20' : 'w-24 h-24'} mx-auto rounded-full border-2 border-primary/20 animate-ping`}></div>
                  </div>
                  <div className="space-y-4">
                    <h2 className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'text-2xl' : 'text-3xl'} font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent`}>
                      {mode === 'buyer' ? 'Discover Amazing Products' : 'Create Perfect Listings'}
                    </h2>
                    <p className={`text-muted-foreground ${messages.length > 0 && recommendationHistory.length > 0 ? 'text-sm max-w-md' : 'text-lg max-w-2xl'} mx-auto leading-relaxed`}>
                      {mode === 'buyer'
                        ? messages.length > 0 && recommendationHistory.length > 0
                          ? 'Try: "Find me vintage sneakers under $100" or "Show me gaming laptops"'
                          : 'Try: "Find me vintage sneakers under $100" or "Show me gaming laptops with good reviews"'
                        : 'Upload photos of your item and I\'ll help create the perfect listing with optimized descriptions'
                      }
                    </p>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}
                >
                  <div
                    className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'max-w-xs lg:max-w-sm' : 'max-w-md lg:max-w-lg'} px-4 py-3 rounded-2xl backdrop-blur-xl border border-border/30 shadow-lg ${
                      message.isUser
                        ? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground'
                        : 'bg-gradient-to-br from-white/10 to-white/5 text-foreground'
                    }`}
                  >
                    <p className={`leading-relaxed ${messages.length > 0 && recommendationHistory.length > 0 ? 'text-sm' : 'text-base'}`}>{message.text}</p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start animate-slide-up">
                  <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-border/30 px-4 py-3 rounded-2xl shadow-lg">
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 text-primary animate-pulse" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce delay-200"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
             </div>
           </div>
         </div>

         {/* Input Area for Chat - Fixed at bottom of chat section */}
         {mode === 'buyer' && (
           <div className="flex-shrink-0 border-t border-border/20 bg-background/80 backdrop-blur-xl p-4">
             <div className={`${messages.length > 0 && recommendationHistory.length > 0 ? 'max-w-2xl' : 'max-w-4xl'} mx-auto`}>
               <div className="flex items-end space-x-3">
                 <Button
                   onClick={toggleMic}
                   variant="outline"
                   size="icon"
                   className="mb-2 border-border/30 bg-background/50 backdrop-blur hover:bg-secondary/10 hover:border-secondary/30"
                 >
                   <Mic className="h-4 w-4" />
                 </Button>
                 
                 <div className="flex-1 relative">
                   <Input
                     onFocus={() => setIsListening(false)}
                     value={inputText}
                     onChange={(e) => setInputText(e.target.value)}
                     onKeyPress={handleKeyPress}
                     placeholder={messages.length > 0 && recommendationHistory.length > 0 ? "Ask me to find products..." : "Ask me to find products... (e.g., 'vintage sneakers under $100')"}
                     className={`pr-16 ${messages.length > 0 && recommendationHistory.length > 0 ? 'h-10 text-sm' : 'h-12 text-base'} bg-background/50 backdrop-blur border-border/30 focus:border-primary/50 focus:bg-background/70 rounded-xl transition-all duration-300`}
                   />
                   <Button
                     onClick={handleSendMessage}
                     disabled={!inputText.trim() || isLoading}
                     className={`absolute right-2 top-1/2 -translate-y-1/2 ${messages.length > 0 && recommendationHistory.length > 0 ? 'h-6 px-3 text-xs' : 'h-8 px-4 text-sm'} bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary shadow-lg transition-all duration-300`}
                   >
                     Send
                   </Button>
                 </div>
               </div>
             </div>
           </div>
         )}

         {/* Future Form Area - For Seller */}
         {mode === 'seller' && (
           <div className="flex-shrink-0 p-6">
             {/* Placeholder for seller form (you can insert form here later) */}
           </div>
         )}
       </div>

       {/* Right Side - Recommendations - Only show when there are messages and recommendations */}
       {messages.length > 0 && recommendationHistory.length > 0 && (
         <div className="w-1/2 overflow-y-auto bg-gradient-to-br from-muted/5 to-muted/10">
           <div className="p-6 h-full">
             <div className="space-y-6">
               <div className="text-center pb-4 border-b border-border/20">
                 <h3 className="text-xl font-semibold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                   Product Recommendations
                 </h3>
               </div>
               
               <div className="space-y-6">
                 {recommendationHistory.map((historyItem, historyIndex) => (
                   <div key={historyIndex} className="space-y-3">
                     {/* Query Header */}
                     <div className="flex items-center justify-between pb-2 border-b border-border/10">
                       <div className="flex items-center space-x-2">
                         <Search className="h-4 w-4 text-primary" />
                         <h4 className="text-sm font-semibold text-foreground">
                           "{historyItem.query}"
                         </h4>
                         <Badge variant="secondary" className="text-xs">
                           {historyItem.recommendations.length}
                         </Badge>
                       </div>
                       <div className="text-xs text-muted-foreground">
                         {historyItem.timestamp.toLocaleTimeString()}
                       </div>
                     </div>
                     
                     {/* Recommendations for this query */}
                     <RecommendationCards recommendations={historyItem.recommendations} handleBidClick={handleBidClick} useCarousel={true} />
                   </div>
                 ))}
               </div>
             </div>
           </div>
         </div>
       )}
     </div>


      {/* Bid Dialog */}
      <Dialog open={bidDialogOpen} onOpenChange={setBidDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Place a Bid</DialogTitle>
          </DialogHeader>
          {selectedProduct && (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-muted/20 rounded-lg">
                {selectedProduct.image_url && (
                  <img
                    src={`${selectedProduct.image_url.startsWith('https') ? selectedProduct.image_url : `http://127.0.0.1:8000${selectedProduct.image_url}`}`}
                    alt={selectedProduct.title}
                    className="w-12 h-12 object-cover rounded"
                  />
                )}
                <div className="flex-1">
                  <h4 className="font-medium line-clamp-1">{selectedProduct.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    Suggested: ${selectedProduct.suggested_price}
                    {selectedProduct.current_bid && ` • Current: $${selectedProduct.current_bid}`}
                  </p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="user_id">Your Name</Label>
                  <Input
                    id="user_id"
                    value={bidFormData.user_id}
                    onChange={(e) => setBidFormData(prev => ({ ...prev, user_id: e.target.value }))}
                    placeholder="Enter your name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="amount">Bid Amount ($)</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={bidFormData.amount}
                    onChange={(e) => setBidFormData(prev => ({ ...prev, amount: e.target.value }))}
                    placeholder="Enter bid amount"
                    min={selectedProduct.current_bid ? selectedProduct.current_bid + 1 : 1}
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-2 pt-4">
                <Button variant="outline" onClick={() => setBidDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleBidSubmit} disabled={!bidFormData.user_id || !bidFormData.amount}>
                  <Gavel className="h-4 w-4 mr-2" />
                  Submit Bid
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

    </div>
  );
};

export default Chat;