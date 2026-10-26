
// Header.jsx
// Application header with logo, navigation, and (optional) action buttons.
import React from 'react'
import { Button } from "@/components/ui/button";
import { cn } from "../lib/utils";



/**
 * Header Component
 * Displays the application header with logo, navigation, and optional action buttons.
 */
const Header = () => {
    return (
        <div style={{ display: 'flex', width: '100%' }}>
            <header className="px-5 w-full sticky top-0 z-50 border-b border-border/40 bg-background/40 backdrop-blur-md supports-[backdrop-filter]:bg-background/20 transition-all duration-300">
                <div className="container mx-auto flex items-center justify-between py-3">
                    {/* Logo and Navigation */}
                    <div className="flex items-center space-x-8">
                        {/* Logo */}
                        <div className="text-2xl font-bold text-primary flex items-center gap-2 tracking-tighter">
                            <span>△</span>
                            <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">AMY</span>
                        </div>
                        {/* Navigation text */}
                        <div className="flex items-center text-sm">
                            <span className="text-muted-foreground">Hii it's </span>
                            <span className="mx-1 font-semibold text-foreground text-lg">Amy, </span>
                            <span className="text-muted-foreground">your internal auditor copilot</span>
                        </div>
                        {/* Navigation links (commented out) */}
                    </div>

                    {/* Action Buttons (commented out) */}
                    <div className="flex space-x-4">
                        {/* <Button variant="outline" className="px-4">
                            Sign in
                        </Button>
                        <Button className="bg-black text-white hover:bg-gray-800 px-4">
                            Sign Up
                        </Button> */}
                    </div>
                </div>
            </header>
        </div>
    )
}

export default Header