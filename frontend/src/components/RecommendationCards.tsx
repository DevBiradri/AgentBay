import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { DollarSign, Gavel } from "lucide-react";

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

type RecommendationCardsProps = {
  recommendations: Recommendation[];
  handleBidClick: (item: Recommendation) => void;
  useCarousel?: boolean; // New prop
};

const RecommendationCards = ({ recommendations, handleBidClick, useCarousel = true }: RecommendationCardsProps) => {
  if (recommendations.length === 0) return null;

  const ProductCard = ({ item }: { item: Recommendation }) => (
    <Card className="group hover:shadow-lg transition-all duration-300 border-border/30 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl h-full max-w-lg">
      {/* Product Image */}
      {item.image_url && (
        <div className="relative h-32 overflow-hidden rounded-t-lg">
          <img
            src={`${item.image_url?.startsWith('https') ? item.image_url : `http://127.0.0.1:8000${item.image_url}`}`}
            alt={item.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      )}
      <CardHeader className="pb-2 px-3 pt-3">
        <CardTitle className="text-sm font-medium line-clamp-2">{item.title}</CardTitle>
        {item.brand && item.model && (
          <p className="text-xs text-muted-foreground">{item.brand} {item.model}</p>
        )}
      </CardHeader>
      <CardContent className="pt-0 px-3 pb-3">
        <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{item.description}</p>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-1">
            <DollarSign className="h-3 w-3 text-primary" />
            <span className="font-semibold text-primary text-sm">${item.suggested_price}</span>
          </div>
          {item.current_bid && (
            <div className="flex items-center space-x-1">
              <span className="text-xs text-muted-foreground">Bid:</span>
              <span className="text-xs font-medium">${item.current_bid}</span>
            </div>
          )}
        </div>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            <Badge variant="outline" className="text-xs px-1 py-0">
              {item.category}
            </Badge>
            {item.tags.slice(0, 2).map((tag, tagIndex) => (
              <Badge key={tagIndex} variant="secondary" className="text-xs px-1 py-0">
                {tag}
              </Badge>
            ))}
          </div>
          {/* Bid Button */}
          <Button
            onClick={() => handleBidClick(item)}
            size="sm"
            className="w-full bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary shadow-lg text-xs"
          >
            <Gavel className="h-3 w-3 mr-1" />
            Place Bid
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="mb-4">
      {useCarousel && recommendations.length > 2 ? (
        // Carousel layout for more than 2 items (adjusted for split screen)
        <Carousel
          opts={{
            align: "start",
            loop: false,
          }}
          className="w-full"
        >
          <CarouselContent className="-ml-2">
            {recommendations.map((item, index) => (
              <CarouselItem key={item.id || index} className="pl-2 basis-full md:basis-1/2">
                <ProductCard item={item} />
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      ) : (
        // Grid layout for all items or 2 or fewer items
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {recommendations.map((item, index) => (
            <ProductCard key={item.id || index} item={item} />
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationCards;