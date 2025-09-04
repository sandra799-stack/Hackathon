"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface FloatingButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
  onClick?: () => void;
  onSuccess?: () => void;
  isLoggedIn?: boolean;
  setShowLoginModal?: (show: boolean) => void;
}

export function FloatingButton({
  className,
  onClick,
  onSuccess,
  isLoggedIn = false,
  setShowLoginModal,
  ...props
}: FloatingButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  const handleClick = async () => {
    if (!isLoggedIn) {
      if (setShowLoginModal) {
        setShowLoginModal(true);
      }
      return;
    }

    setIsProcessing(true);

    try {
      const merchantId = localStorage.getItem("user_id");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/recommendations/campaigns/${merchantId}`
      );

      if (!response.ok) {
        throw new Error("Failed to get recommendations");
      }

      setIsProcessing(false);
      toast({
        title: "Promotions activated",
        description: "Your promotions have been activated successfully!",
      });

      if (onClick) {
        onClick();
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setIsProcessing(false);
      toast({
        title: "Error",
        description: "Failed to activate promotions. Please try again.",
        variant: "destructive",
      });
    }
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
      <TooltipContent
        side="left"
        className="bg-primary/90 text-primary-foreground text-sm p-2"
      >
        Automatically activate promotions based on your sales history
      </TooltipContent>
    </Tooltip>
  );
}
