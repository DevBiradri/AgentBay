import { useState , useEffect} from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Camera, Search, MessageCircle, Upload, Shield, Sparkles, Mic, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

type Mode = 'selection' | 'buyer' | 'seller';
type ChatMessage = {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
};

const Chat = () => {
  const [mode, setMode] = useState<Mode>('selection');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // mic listening state
  const [isListening, setIsListening] = useState(false);
  const navigate = useNavigate();

  // 
  
  useEffect(() => {
    console.log('Listening state changed:', isListening);
  }, [isListening]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: mode === 'buyer' 
          ? "I found several vintage sneakers under $100. Here are my top recommendations with fraud detection analysis..."
          : "I'll help you create an optimized listing. Please upload photos of your item and I'll generate a compelling description.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
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
  };

  if (mode === 'selection') {
    return (
    
      <div className="min-h-screen bg-background flex flex-col">
        {/* Header */}
        <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-16 items-center">
            <Button variant="ghost" onClick={() => navigate('/')} className="mr-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                AIMarket Chat
              </span>
            </div>
          </div>
        </nav>

        {/* Mode Selection */}
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full space-y-8 text-center">
            <div className="space-y-4">
              <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto">
                <MessageCircle className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold">How can I help you today?</h1>
              <p className="text-muted-foreground">
                Choose your mode to get started with AI-powered assistance
              </p>
            </div>

            <div className="space-y-4">
              <Card 
                className="p-6 cursor-pointer transition-all duration-300 hover:shadow-product group border-2 hover:border-primary/20"
                onClick={() => setMode('buyer')}
              >
                <CardContent className="p-0 space-y-3">
                  <div className="w-12 h-12 bg-gradient-secondary rounded-lg flex items-center justify-center">
                    <Search className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-lg">I'm Looking to Buy</h3>
                    <p className="text-muted-foreground text-sm">
                      Search products with voice or text, get AI recommendations with fraud detection
                    </p>
                  </div>
                  <Badge variant="outline" className="w-fit">
                    <Shield className="w-3 h-3 mr-1" />
                    Fraud Protection
                  </Badge>
                </CardContent>
              </Card>

              <Card 
                className="p-6 cursor-pointer transition-all duration-300 hover:shadow-product group border-2 hover:border-primary/20"
                onClick={() => setMode('seller')}
              >
                <CardContent className="p-0 space-y-3">
                  <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
                    <Camera className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-lg">I Want to Sell</h3>
                    <p className="text-muted-foreground text-sm">
                      Upload photos and get AI-generated descriptions and pricing suggestions
                    </p>
                  </div>
                  <Badge variant="outline" className="w-fit">
                    <Sparkles className="w-3 h-3 mr-1" />
                    AI Descriptions
                  </Badge>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen  bg-background flex flex-col">
    

      {/* Header */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <Button variant="ghost" onClick={resetToSelection} className="mr-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex items-center space-x-2">
            {mode === 'buyer' ? (
              <Search className="h-5 w-5 text-secondary" />
            ) : (
              <Camera className="h-5 w-5 text-primary" />
            )}
            <span className="font-semibold">
              {mode === 'buyer' ? 'Buyer Mode' : 'Seller Mode'}
            </span>
          </div>
          <Badge variant="outline" className="ml-auto">
            {mode === 'buyer' ? 'Shopping Assistant' : 'Listing Helper'}
          </Badge>
        </div>
      </nav>
    

      {/* Chat Messages */}
      <div className={`flex-1 overflow-auto-y ${isListening?'mic-active':''}`}>
                      {/* mic listening custom animated ui */}
      
      {isListening && (
      <div className="listening-overlay fixed  mt-5 mt-20 h-[100%] w-full flex items-center justify-center z-50">
         <div className="listening-circle">
      <Mic className="h-12 w-12 text-white" onClick={()=>setIsListening(l=>!l)} />
    </div>
  </div>
    )}

        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center space-y-4 py-12">
              <div className={`w-16 h-16 ${mode === 'buyer' ? 'bg-gradient-secondary' : 'bg-gradient-primary'} rounded-full flex items-center justify-center mx-auto`}>
                {mode === 'buyer' ? (
                  <Search className="w-8 h-8 text-white" />
                ) : (
                  <Camera className="w-8 h-8 text-white" />
                )}
              </div>
    
              <div>
                
                <h2 className="text-xl font-semibold mb-2">
                  {mode === 'buyer' ? 'Find Your Perfect Product' : 'Create Your Listing'}
                </h2>
                <p className="text-muted-foreground">
                  {mode === 'buyer' 
                    ? 'Try: "Find me vintage sneakers under $100" or "Show me gaming laptops with good reviews"'
                    : 'Upload photos of your item and I\'ll help create the perfect listing'
                  }
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isUser
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse delay-100"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse delay-200"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex space-x-2">
            {mode === 'seller' && (
              <Button variant="outline" size="icon">
                <Upload className="h-4 w-4" />
              </Button>
            )}
            {mode === 'buyer' && (
              <Button variant="outline" size="icon" onClick={()=>setIsListening(l=>!l)}>
                <Mic className="h-4 w-4" />
                
              </Button>
            )}
            <Input
              value={inputText}
              onFocus={()=>setIsListening(false)}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                mode === 'buyer'
                  ? "Ask me to find products... (e.g., 'vintage sneakers under $100')"
                  : "Describe your item or upload photos..."
              }
              className="flex-1"
            />
            <Button 
              onClick={handleSendMessage} 
              disabled={!inputText.trim() || isLoading}
              className="px-6"
            >
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;