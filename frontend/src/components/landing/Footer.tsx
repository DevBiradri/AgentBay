import { Sparkles } from "lucide-react";

const Footer = () => {
  return (
    <footer className="border-t py-12 bg-muted/30">
      <div className="container max-w-6xl">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AgentBay</span>
          </div>
          <p className="text-muted-foreground">
            © 2024 AgentBay. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;