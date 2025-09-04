"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface FloatingButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
  onClick?: () => void;
}

export function FloatingButton({
  className,
  onClick,
  ...props
}: FloatingButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  const handleClick = () => {
    setIsProcessing(true);

    setTimeout(() => {
      setIsProcessing(false);
      toast({
        title: "AI Agent",
        description: "Your request has been processed successfully!",
      });

      if (onClick) {
        onClick();
      }
    }, 1500);
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div
          className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full border-2 border-primary flex items-center justify-center cursor-pointer bg-background"
          onClick={handleClick}
        >
          {isProcessing ? (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          ) : (
            <Sparkles
              className="animate-pulse text-primary"
              width={350}
              style={{
                width: 350,
                animationDuration: "2s",
              }}
            />
          )}
        </div>
      </TooltipTrigger>
      <TooltipContent side="left" className="bg-primary/90 text-primary-foreground text-sm p-2">
        Automatically activate promotions based on your sales history
      </TooltipContent>
    </Tooltip>
  );
}
