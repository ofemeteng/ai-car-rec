import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Recommendation } from "@/lib/types";
// import { Stars } from "@/components/Stars"; // Keep if you plan to use it
import { Info } from "lucide-react"; // MapPin removed as it wasn't used
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

type RecommendationCardProps = {
  recommendation: Recommendation;
  className?: string;
  number?: number;
  actions?: ReactNode;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
};

export function RecommendationCard({
  recommendation,
  actions,
  onMouseEnter,
  onMouseLeave,
  className,
  number,
}: RecommendationCardProps) {
  return (
    <Card
      className={cn(
        "bg-background rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 ease-in-out", // Enhanced base and hover shadow, explicit border and rounding
        className
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <CardContent className="p-6"> {/* Consistent padding */}
        <div className="flex flex-col space-y-4"> {/* Changed to flex-col for potentially better control with actions */}
          <div className="flex justify-between items-start gap-4"> {/* Added gap for actions */}
            <div className="flex-grow space-y-1.5"> {/* Reduced space-y for tighter title group */}
              <CardTitle className="text-lg md:text-xl font-bold flex items-center gap-3"> {/* Adjusted font size, weight and gap */}
                {number && (
                  <div
                    className="flex-shrink-0 text-xs bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold w-8 h-8 border-2 border-background ring-1 ring-primary/50" // Enhanced styling for number
                  >
                    {number}
                  </div>
                )}
                <span className="leading-tight">{recommendation.car}</span> {/* Ensured title text is wrapped in a span for better control if needed */}
              </CardTitle>
              {/* <Stars rating={place.rating} /> */}
            </div>
            {actions && <div className="flex-shrink-0">{actions}</div>} {/* Ensure actions don't cause overflow if title is long */}
          </div>

          <div className="space-y-3 text-sm"> {/* Increased base space-y here */}
            {recommendation.tagline && ( // Check if tagline exists
              <p className="italic text-muted-foreground"> {/* Made tagline italic */}
                "{recommendation.tagline}" {/* Added quotes for emphasis */}
              </p>
            )}

            {recommendation.content && (
              <div className="flex items-start gap-2 pt-1 text-foreground/80"> {/* text-foreground/80 for better readability than muted, items-start for multi-line content */}
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" /> {/* Icon color and alignment */}
                <p className="flex-1">{recommendation.content}</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}