const HowItWorksSection = () => {
  return (
    <section className="py-24">
      <div className="container max-w-4xl text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-16">
          How It Works
        </h2>
        <div className="grid md:grid-cols-2 gap-12">
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-[#2463eb]">For Sellers</h3>
            <div className="space-y-4 text-left">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#2463eb] rounded-full flex items-center justify-center text-white font-bold text-sm">1</div>
                <div>
                  <h4 className="font-semibold">Upload Photos</h4>
                  <p className="text-muted-foreground">Take or upload photos of your items</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#2463eb] rounded-full flex items-center justify-center text-white font-bold text-sm">2</div>
                <div>
                  <h4 className="font-semibold">AI Description</h4>
                  <p className="text-muted-foreground">Our AI creates compelling product descriptions</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#2463eb] rounded-full flex items-center justify-center text-white font-bold text-sm">3</div>
                <div>
                  <h4 className="font-semibold">Review & Publish</h4>
                  <p className="text-muted-foreground">Review, edit if needed, and publish your listing</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-[#14522d ]">For Buyers</h3>
            <div className="space-y-4 text-left">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#14522d] rounded-full flex items-center justify-center text-white font-bold text-sm">1</div>
                <div>
                  <h4 className="font-semibold">Search Products</h4>
                  <p className="text-muted-foreground">Use voice or text to find what you need</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#14522d] rounded-full flex items-center justify-center text-white font-bold text-sm">2</div>
                <div>
                  <h4 className="font-semibold">AI Suggestions</h4>
                  <p className="text-muted-foreground">Get personalized recommendations</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#14522d] rounded-full flex items-center justify-center text-white font-bold text-sm">3</div>
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
  );
};

export default HowItWorksSection;