
import { Button } from "@/components/ui/button";
import { ArrowLeft, Bot, Gavel } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ThemeToggle } from "@/components/ui/theme-toggle";

import  ArchitectureSVG from "@/assets/architecture.svg";

export const Architecture = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
     
      <nav className="relative z-10 border-b border-border/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mr-4 hover:bg-primary/10"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>

          <div className="flex items-center space-x-3">
            <div className="relative">
              <Bot className="h-8 w-8 text-primary animate-pulse dark:text-primary" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full animate-ping"></div>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              System Architecture
            </span>
          </div>

          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </div>
      </nav>

      <h1 className="w-full text-center mt-10 text-[5vw] font-bold text-black dark:text-white">
  AI Agents Architecture
</h1>
      <div className=" flex  justify-center overflow-auto">
      <img className="w-[60%] " src={ArchitectureSVG} alt="Architecture" />
      </div>
    </div>
   
  );
};