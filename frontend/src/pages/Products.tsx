import { useEffect, useState } from "react";
import axios from "axios";
import RecommendationCards from "@/components/RecommendationCards";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge"; // Added Badge import
import { ArrowLeft, Bot, Gavel } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import Swal from 'sweetalert2';

type Recommendation = {
  id?: number;
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

const Products = () => {
  const [products, setProducts] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [bidDialogOpen, setBidDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Recommendation | null>(null);
  const [bidFormData, setBidFormData] = useState({
    user_id: '',
    amount: ''
  });
  const [viewBidsDialogOpen, setViewBidsDialogOpen] = useState(false);
  const [bidsData, setBidsData] = useState<any>(null); // To store bids for a product

  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/products")
      .then((response) => {
        console.log("API Response:", response.data);
        setProducts(response.data || []);
      })
      .catch((error) => {
        console.error("Error fetching products:", error);
      })
      .finally(() => setLoading(false));
  }, []); // Correctly close useEffect

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
        customClass: {
          popup: 'swal-glass'
        },
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
        customClass: {
          popup: 'swal-glass'
        },
        text: 'Failed to place bid. Please try again.',
        icon: 'error',
        confirmButtonText: 'OK',
        confirmButtonColor: '#ef4444',
        background: 'var(--background)',
        color: 'var(--foreground)',
      });
    }
  };

  const handleViewBidsClick = async (product: Recommendation) => {
    if (!product.id) return;
    try {
      const response = await axios.get(`http://localhost:8000/api/products/${product.id}/bids`);
      setBidsData(response.data);
      setViewBidsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching bids:', error);
      Swal.fire({
        title: 'Error!',
        customClass: {
          popup: 'swal-glass'
        },
        text: 'Failed to fetch bids. Please try again later.',
        icon: 'error',
        confirmButtonColor: '#ef4444'
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header/Navbar */}
      <nav className="relative z-10 border-b border-border/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <Button
            variant="ghost"
            onClick={() => navigate("/chat")}
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
              Products
            </span>
          </div>

          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <div className="p-8">
        {loading ? (
          <div>Loading...</div>
        ) : (
          <RecommendationCards recommendations={products} handleBidClick={handleBidClick} onViewBidsClick={handleViewBidsClick} useCarousel={false} />
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

      {/* View Bids Dialog */}
      <Dialog open={viewBidsDialogOpen} onOpenChange={setViewBidsDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Bids for {selectedProduct?.title}</DialogTitle>
          </DialogHeader>
          {bidsData && bidsData.bids && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">Total Bids: {bidsData.bid_count}</p>
              {bidsData.bids.length > 0 ? (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {bidsData.bids.map((bid: any, index: number) => (
                    <div key={index} className="flex justify-between items-center p-2 border rounded-lg">
                      <div>
                        <p className="font-medium">{bid.user_id}</p>
                        <p className="text-sm text-muted-foreground">${bid.amount} - {new Date(bid.timestamp).toLocaleString()}</p>
                      </div>
                      <Badge variant={bid.status === 'winning' ? 'default' : 'secondary'}>
                        {bid.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No bids yet for this product.</p>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Products;