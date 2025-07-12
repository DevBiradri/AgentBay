import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Camera, Search, MessageCircle, Upload, Shield, Sparkles, Mic, ArrowLeft, Bot } from "lucide-react";
import { useNavigate } from "react-router-dom";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
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
  const [isListening, setIsListening] = useState(false);
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
              <div className="relative">
                <Bot className="h-8 w-8 text-primary animate-pulse" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full animate-ping"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                AI Assistant
              </span>
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

            <div className="grid md:grid-cols-2 gap-6">
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
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 relative overflow-hidden">
      {/* Futuristic background elements */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="absolute top-0 left-1/3 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-0 right-1/3 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse"></div>

      {/* Header */}
      <nav className="relative z-10 border-b border-border/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
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
          </div>
        </div>
      </nav>

      {/* Chat Messages */}
      <div className="relative z-10 flex-1 overflow-y-auto p min-h-[calc(100vh-11rem)]">
     
                      {/* mic listening custom animated ui */}
      
      {isListening && (
      <div className="listening-overlay fixed  h-[80%]  mt-20  w-full  flex items-center justify-center z-50">
         <div className="listening-circle">
      <Mic className="h-12 w-12 text-white" onClick={()=>setIsListening(l=>!l)} />
    </div>
  </div>
    )}
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center space-y-8 py-16">
              <div className="relative">
                <div className={`w-24 h-24 ${mode === 'buyer' ? 'bg-gradient-to-br from-secondary to-secondary/80' : 'bg-gradient-to-br from-primary to-primary/80'} rounded-full flex items-center justify-center mx-auto shadow-glow animate-float`}>
                  {mode === 'buyer' ? (
                    <Search className="w-12 h-12 text-white" />
                  ) : (
                    <Camera className="w-12 h-12 text-white" />
                  )}
                </div>
                <div className="absolute inset-0 w-24 h-24 mx-auto rounded-full border-2 border-primary/20 animate-ping"></div>
              </div>
              <div className="space-y-4">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                  {mode === 'buyer' ? 'Discover Amazing Products' : 'Create Perfect Listings'}
                </h2>
                <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
                  {mode === 'buyer' 
                    ? 'Try: "Find me vintage sneakers under $100" or "Show me gaming laptops with good reviews"'
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
                className={`max-w-md lg:max-w-lg px-6 py-4 rounded-2xl backdrop-blur-xl border border-border/30 shadow-lg ${
                  message.isUser
                    ? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground'
                    : 'bg-gradient-to-br from-white/10 to-white/5 text-foreground'
                }`}
              >
                <p className="leading-relaxed">{message.text}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-slide-up">
              <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-border/30 px-6 py-4 rounded-2xl shadow-lg">
                <div className="flex items-center space-x-2">
                  <Bot className="w-5 h-5 text-primary animate-pulse" />
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

      {/* Input Area */}
      <div className="relative z-10 border-t border-border/20 bg-background/80 backdrop-blur-xl p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            {mode === 'seller' && (
              <Button 
                variant="outline" 
                size="icon" 
                className="mb-2 border-border/30 bg-background/50 backdrop-blur hover:bg-primary/10 hover:border-primary/30"
              >
                <Upload className="h-4 w-4" />
              </Button>
            )}
            {mode === 'buyer' && (
              <Button 
              onClick={toggleMic}
                variant="outline" 
                size="icon" 
                className="mb-2 border-border/30 bg-background/50 backdrop-blur hover:bg-secondary/10 hover:border-secondary/30"
              >
                <Mic className="h-4 w-4"  />
              </Button>
            )}
            <div className="flex-1 relative">
              <Input
                onFocus={()=>setIsListening(false)}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  mode === 'buyer'
                    ? "Ask me to find products... (e.g., 'vintage sneakers under $100')"
                    : "Describe your item or upload photos..."
                }
                className="pr-16 h-12 bg-background/50 backdrop-blur border-border/30 focus:border-primary/50 focus:bg-background/70 rounded-xl"
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={!inputText.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 px-4 bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary shadow-lg"
              >
                Send
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;