import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Navigation = () => {
  const navigate = useNavigate();

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-16 items-center">
        <div className="flex items-center space-x-2" onClick={()=>navigate('/')}>
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent" >
            AgentBay
          </span>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <Button variant="ghost" onClick={()=> navigate('/signin')}>Sign In</Button>
          <Button variant="hero" onClick={() => navigate('/chat')}>Get Started</Button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;