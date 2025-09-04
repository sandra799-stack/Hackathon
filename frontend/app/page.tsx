"use client";

import type React from "react";

import { useEffect, useState } from "react";
import {
  Search,
  Clock,
  Star,
  Users,
  Share2,
  Target,
  X,
  CloudSun,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { FloatingButton } from "@/components/ui/floating-button";

interface Coupon {
  id: number;
  promotion_name: string;
  description: string;
  icon: string;
  is_active: boolean;
}

const LoginModal = ({
  isOpen,
  onClose,
  onLogin,
}: {
  isOpen: boolean;
  onClose: () => void;
  onLogin: () => void;
}) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim() === "loving_user" && password.trim() === "123456") {
      localStorage.setItem("user_id", "1");
      onLogin();
      setUsername("");
      setPassword("");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background border-2 border-border rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-foreground">Login Required</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-muted-foreground mb-6">
          Please log in to activate promotions and enjoy exclusive perks!
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Username
            </label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full"
              required
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Password
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full"
              required
            />
          </div>
          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              className="flex-1 bg-accent text-accent-foreground hover:bg-accent/80"
            >
              Log In
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 bg-transparent"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

const LovingLoyaltyLogo = () => (
  <div className="w-32 h-24 flex items-center justify-center">
    <img
      src="/loving-loyalty-logo.svg"
      alt="Loving Loyalty Logo"
      className="w-32 h-24 object-contain brightness-0 invert"
    />
  </div>
);

const AnimatedCake = () => (
  <div className="w-8 h-8 relative animate-bounce">
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-8 h-8"
    >
      <path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8" />
      <path d="M3 21h18" />
      <path d="M7 8v3" />
      <path d="M12 8v3" />
      <path d="M17 8v3" />
      <path d="M7 4h.01" />
      <path d="M12 4h.01" />
      <path d="M17 4h.01" />
    </svg>
  </div>
);

const AnimatedUsers = () => (
  <div className="w-8 h-8 relative animate-pulse">
    <Users className="w-8 h-8" />
  </div>
);

const AnimatedShare2 = () => (
  <div
    className="w-8 h-8 relative animate-pulse"
    style={{ animationDuration: "2s" }}
  >
    <Share2 className="w-8 h-8" />
  </div>
);

const AnimatedStar = () => (
  <div className="relative">
    <Star className="w-8 h-8 animate-ping absolute" />
    <Star className="w-8 h-8 relative" />
  </div>
);

const AnimatedClock = () => (
  <div
    className="w-8 h-8 relative animate-bounce"
    style={{ animationDelay: "0.5s" }}
  >
    <Clock className="w-8 h-8" />
  </div>
);

const AnimatedTarget = () => (
  <div
    className="w-8 h-8 relative animate-pulse"
    style={{ animationDelay: "1s" }}
  >
    <Target className="w-8 h-8" />
  </div>
);

const AnimatedSunCloud = () => (
  <div
    className="w-8 h-8 relative animate-pulse"
    style={{ animationDelay: "1s" }}
  >
    <CloudSun className="w-8 h-8" />
  </div>
);

const getIconComponent = (iconName: string): React.ReactNode => {
  switch (iconName) {
    case "AnimatedCake":
      return <AnimatedCake />;
    case "AnimatedUsers":
      return <AnimatedUsers />;
    case "AnimatedShare2":
      return <AnimatedShare2 />;
    case "AnimatedStar":
      return <AnimatedStar />;
    case "AnimatedClock":
      return <AnimatedClock />;
    case "AnimatedTarget":
      return <AnimatedTarget />;
    case "AnimatedSunCloud":
      return <AnimatedSunCloud />;
    default:
      return <AnimatedStar />;
  }
};

const fetchPromotions = async (merchantId: string): Promise<Coupon[]> => {
  try {
    // Use the Next.js API route as a proxy
    const response = await fetch(`/api/promotions/${merchantId}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error("Failed to fetch promotions");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    throw error;
  }
};

const scheduleJob = async (
  merchantId: string,
  promotionName: string
): Promise<void> => {
  try {
    const transformedName = promotionName.toLowerCase().replace(/\s+/g, "-");
    // Use the Next.js API route as a proxy
    const response = await fetch(`/api/schedule-job/${merchantId}/${transformedName}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error("Failed to schedule job");
    }
  } catch (error) {
    throw error;
  }
};

const deleteJob = async (
  merchantId: string,
  promotionName: string
): Promise<void> => {
  try {
    const transformedName = promotionName.toLowerCase().replace(/\s+/g, "-");
    // Use the Next.js API route as a proxy
    const response = await fetch(`/api/delete-job/${merchantId}/${transformedName}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      throw new Error("Failed to delete job");
    }
  } catch (error) {
    throw error;
  }
};

export default function CouponsPage() {
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [activatedCoupons, setActivatedCoupons] = useState<Coupon[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activatingCoupons, setActivatingCoupons] = useState<Set<number>>(
    new Set()
  );
  const [removingCoupons, setRemovingCoupons] = useState<Set<number>>(
    new Set()
  );

  const filteredCoupons = coupons.filter(
    (coupon) =>
      coupon.promotion_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      coupon.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const availableCoupons = isLoggedIn
    ? filteredCoupons.filter(
        (coupon) =>
          !coupon.is_active &&
          !activatedCoupons.some((activated) => activated.id === coupon.id)
      )
    : filteredCoupons;

  const activateCoupon = async (coupon: Coupon) => {
    if (!isLoggedIn) {
      setShowLoginModal(true);
      return;
    }

    if (activatingCoupons.has(coupon.id)) {
      return;
    }

    setActivatingCoupons((prev) => new Set(prev).add(coupon.id));

    try {
      const merchantId = localStorage.getItem("user_id");
      if (merchantId) {
        await scheduleJob(merchantId, coupon.promotion_name);
        // Refresh promotions list to get updated state
        const promotions = await fetchPromotions("1");
        setCoupons(promotions);
        const activeCoupons = promotions.filter((coupon) => coupon.is_active);
        setActivatedCoupons(activeCoupons);

        toast({
          title: "Coupon Removed!",
          description: `${coupon.promotion_name} has been successfully removed.`,
          variant: "success",
        });
        setSearchTerm("");

        toast({
          title: "Coupon Activated!",
          description: `${coupon.promotion_name} has been successfully activated.`,
          variant: "success",
        });
      }
    } catch {
      toast({
        title: "Activation Failed!",
        description: `Failed to activate ${coupon.promotion_name}. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setActivatingCoupons((prev) => {
        const newSet = new Set(prev);
        newSet.delete(coupon.id);
        return newSet;
      });
    }
  };

  const deactivateCoupon = async (coupon: Coupon) => {
    if (!isLoggedIn) {
      setShowLoginModal(true);
      return;
    }

    setRemovingCoupons((prev) => new Set(prev).add(coupon.id));

    try {
      const merchantId = localStorage.getItem("user_id");
      if (merchantId) {
        await deleteJob(merchantId, coupon.promotion_name);
        // Refresh promotions list to get updated state
        const promotions = await fetchPromotions("1");
        setCoupons(promotions);
        const activeCoupons = promotions.filter((coupon) => coupon.is_active);
        setActivatedCoupons(activeCoupons);

        toast({
          title: "Coupon Removed!",
          description: `${coupon.promotion_name} has been successfully removed.`,
          variant: "success",
        });
      }
    } catch {
      toast({
        title: "Removal Failed!",
        description: `Failed to remove ${coupon.promotion_name}. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setRemovingCoupons((prev) => {
        const newSet = new Set(prev);
        newSet.delete(coupon.id);
        return newSet;
      });
    }
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
    setShowLoginModal(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setActivatedCoupons([]);
    localStorage.removeItem("user_id");
  };

  useEffect(() => {
    const user_id = localStorage.getItem("user_id");
    if (user_id) {
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    const loadPromotions = async () => {
      setLoading(true);
      setError(null);
      try {
        // Always fetch promotions with hardcoded merchantId '1'
        const promotions = await fetchPromotions("1");
        setCoupons(promotions);

        // Only show activated coupons if user is logged in
        if (isLoggedIn) {
          const activeCoupons = promotions.filter((coupon) => coupon.is_active);
          setActivatedCoupons(activeCoupons);
        } else {
          setActivatedCoupons([]);
        }
      } catch {
        setError("Failed to load promotions");
      } finally {
        setLoading(false);
      }
    };

    loadPromotions();
  }, [isLoggedIn]);

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground py-6 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center space-x-3">
              <LovingLoyaltyLogo />
            </div>
            <div className="flex items-center">
              {isLoggedIn ? (
                <div className="flex items-center gap-4">
                  <span className="text-sm opacity-90">
                    Welcome back, Loving_user!
                  </span>
                  <Button
                    variant="outline"
                    size="default"
                    onClick={handleLogout}
                    className="text-primary bg-white hover:bg-gray-100"
                  >
                    Log Out
                  </Button>
                </div>
              ) : (
                <Button
                  variant="outline"
                  size="default"
                  onClick={() => setShowLoginModal(true)}
                  className="text-primary bg-white hover:bg-gray-50 hover:text-primary hover:shadow-lg transition-all duration-200"
                >
                  Log in to your account
                </Button>
              )}
            </div>
          </div>

          <h1 className="text-4xl font-bold text-center mb-2">
            🎉 Promotion and Marketing
          </h1>
          <p className="text-center text-lg opacity-90">
            Discover amazing deals and activate your favorite perks!
          </p>
        </div>
      </header>

      <div
        className="max-w-6xl mx-auto px-4 py-8"
        style={{ display: !coupons.length ? "none" : "" }}
      >
        {activatedCoupons.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-foreground mb-6 text-center">
              🎊 Activated Promotions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {activatedCoupons.map((coupon) => (
                <Card
                  key={coupon.id}
                  className="h-auto flex flex-col bg-muted border-2 border-accent shadow-md"
                >
                  <CardContent className="p-6 text-center">
                    <div className="text-accent mb-4 flex justify-center">
                      {getIconComponent(coupon.icon)}
                    </div>
                    <h3 className="font-bold text-lg text-card-foreground mb-2">
                      {coupon.promotion_name}
                    </h3>
                    <p className="text-muted-foreground text-sm mb-4">
                      {coupon.description}
                    </p>
                    <Button
                      variant="outline"
                      size="default"
                      onClick={() => deactivateCoupon(coupon)}
                      disabled={removingCoupons.has(coupon.id)}
                      className="text-sm"
                    >
                      {removingCoupons.has(coupon.id) ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                          Removing...
                        </>
                      ) : (
                        "Remove"
                      )}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        )}

        <div className="mb-8">
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
            <Input
              type="text"
              placeholder="Search promotions by name, category, or description"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-3 text-base rounded-lg border-2 border-border focus:border-primary transition-colors w-full placeholder:text-muted-foreground/70"
            />
          </div>
        </div>
        <section className="mb-12">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-foreground">
              Available Promotions
            </h2>
          </div>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground text-lg">
                Loading promotions...
              </p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-500 text-lg mb-4">{error}</p>
              <Button
                onClick={() => {
                  const user_id = localStorage.getItem("user_id");
                  if (user_id && isLoggedIn) {
                    setLoading(true);
                    setError(null);
                    fetchPromotions(user_id)
                      .then((promotions) => {
                        setCoupons(promotions);
                        const activeCoupons = promotions.filter((coupon) => coupon.is_active);
                        setActivatedCoupons(activeCoupons);
                      })
                      .catch(() => setError("Failed to load promotions"))
                      .finally(() => setLoading(false));
                  }
                }}
                variant="outline"
              >
                Try Again
              </Button>
            </div>
          ) : availableCoupons.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg">
                {searchTerm
                  ? "No promotions match your search. Try different keywords!"
                  : "All promotions have been activated! 🎉"}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {availableCoupons.map((coupon) => (
                <Card
                  key={coupon.id}
                  className="hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 border-border hover:border-primary h-auto flex flex-col hover:bg-accent group"
                >
                  <CardContent className="p-6 text-center flex-1 flex flex-col justify-between">
                    <div>
                      <div className="text-primary mb-4 flex justify-center group-hover:text-white">
                        {getIconComponent(coupon.icon)}
                      </div>
                      <h3 className="font-bold text-lg text-card-foreground mb-2 group-hover:text-white">
                        {coupon.promotion_name}
                      </h3>
                      <p className="text-muted-foreground text-sm mb-4 group-hover:text-white/90">
                        {coupon.description}
                      </p>
                    </div>
                    <div>
                      <Button
                        onClick={() => activateCoupon(coupon)}
                        disabled={activatingCoupons.has(coupon.id)}
                        className="bg-accent text-accent-foreground hover:bg-accent/80 transition-colors duration-200 group-hover:bg-white group-hover:text-accent group-hover:hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {activatingCoupons.has(coupon.id) ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                            Activating...
                          </>
                        ) : (
                          "Activate"
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>

      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onLogin={handleLogin}
      />

      <FloatingButton
        isLoggedIn={isLoggedIn}
        setShowLoginModal={setShowLoginModal}
        onSuccess={async () => {
          try {
            const merchantId = localStorage.getItem("user_id") || "1";
            const promotions = await fetchPromotions(merchantId);
            setCoupons(promotions);
            const activeCoupons = promotions.filter(
              (coupon) => coupon.is_active
            );
            setActivatedCoupons(activeCoupons);
          } catch (error) {
            console.error("Error refreshing promotions:", error);
          }
        }}
      />
    </div>
  );
}
