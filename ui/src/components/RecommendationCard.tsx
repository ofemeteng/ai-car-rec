import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Recommendation } from "@/lib/types";
import { Info, Save, MoreHorizontal } from "lucide-react";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type RecommendationCardProps = {
  recommendation: Recommendation;
  className?: string;
  number?: number;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
};

export function RecommendationCard({
  recommendation,
  onMouseEnter,
  onMouseLeave,
  className,
  number,
}: RecommendationCardProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleSave = () => {
    console.log("Saving to Lens:", recommendation);
  };

  return (
    <Card
      className={cn(
        "bg-background rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 ease-in-out",
        className
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <CardContent className="p-6">
        <div className="flex flex-col space-y-4">
          <div className="flex justify-between items-start gap-4">
            <div className="flex-grow space-y-1.5">
              <CardTitle className="text-lg md:text-xl font-bold flex items-center gap-3">
                {number && (
                  <div className="flex-shrink-0 text-xs bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold w-8 h-8 border-2 border-background ring-1 ring-primary/50">
                    {number}
                  </div>
                )}
                <span className="leading-tight">{recommendation.car}</span>
              </CardTitle>
            </div>
            <div className="flex-shrink-0">
              <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={handleSave} className="text-primary">
                    <Save className="w-4 h-4 mr-2" />
                    Save to Lens
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            {recommendation.tagline && (
              <p className="italic text-muted-foreground">
                "{recommendation.tagline}"
              </p>
            )}
            {recommendation.content && (
              <div className="flex items-start gap-2 pt-1 text-foreground/80">
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
                <p className="flex-1">{recommendation.content}</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
