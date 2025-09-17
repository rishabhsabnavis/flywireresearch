import * as React from "react"
import * as SwitchPrimitive from "@radix-ui/react-switch"

import { cn } from "@/lib/utils"

function Switch({
  className,
  ...props
}: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      data-slot="switch"
      className={cn(
        "peer inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-all duration-300 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
        "data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-slate-700",
        "hover:data-[state=checked]:bg-blue-500 hover:data-[state=unchecked]:bg-slate-600",
        "shadow-lg shadow-slate-900/20",
        "switch-enhanced",
        "data-[state=checked]:animate-pulse-slow",
        "p-0.5",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        data-slot="switch-thumb"
        className={cn(
          "pointer-events-none block h-5 w-5 rounded-full bg-white shadow-lg ring-0 transition-all duration-300 ease-in-out",
          "data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0",
          "data-[state=checked]:shadow-blue-500/50 data-[state=unchecked]:shadow-slate-500/50",
          "hover:scale-105 active:scale-95",
          "data-[state=checked]:animate-thumbBounce"
        )}
      />
    </SwitchPrimitive.Root>
  )
}

export { Switch }
