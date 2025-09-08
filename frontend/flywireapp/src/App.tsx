import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useState } from 'react'
import { Switch } from '@/components/ui/switch'
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import { Brain, Search, Database, Activity, AlertCircle, Loader2 } from 'lucide-react'

import './index.css'
import './App.css'

function App() {
  const [rootId, setRootId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [neuronInfo, setNeuronInfo] = useState(null)
  
  const API_BASE_URL = 'http://localhost:8002'

  const handleSubmit = async () => {
    if (!rootId.trim()) {
      setError('Root ID is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const infoResponse = await fetch(`${API_BASE_URL}/neuron_info/${rootId}`)
      const neuronInfo = await infoResponse.json()

      if(neuronInfo.error) {
        throw new Error(neuronInfo.error)
      }
      setNeuronInfo(neuronInfo)
    }
    catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setNeuronInfo(null)
    }
    finally {
      setLoading(false)
    } 
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Flywire Research</h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">Neural Network Analysis Platform</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Flywire</span>
                <Switch />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Neuprint</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Explore Neural Networks
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Analyze neuron connectivity and morphology using the Flywire dataset. 
              Enter a root ID to explore detailed neuron information.
            </p>
          </div>

          {/* Search Form */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 mb-8 hover-lift animate-fade-in-up">
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
                  Neuron Search
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Enter a root ID to retrieve detailed neuron information
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label htmlFor="rootId" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Root ID
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      id="rootId"
                      type="text"
                      placeholder="Enter neuron root ID..."
                      value={rootId}
                      onChange={(e) => setRootId(e.target.value)}
                      className="pl-10 h-12 text-lg"
                      onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                    />
                  </div>
                </div>

                <Button 
                  onClick={handleSubmit} 
                  disabled={loading || !rootId.trim()}
                  className="w-full h-12 text-lg font-semibold"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Database className="mr-2 h-5 w-5" />
                      Analyze Neuron
                    </>
                  )}
                </Button>
              </div>

              {/* Error Display */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mr-2" />
                    <p className="text-red-800 dark:text-red-200 font-medium">{error}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          {neuronInfo && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 animate-fade-in-up">
              <div className="flex items-center mb-6">
                <Activity className="h-6 w-6 text-green-600 mr-2" />
                <h3 className="text-2xl font-semibold text-slate-900 dark:text-white">
                  Neuron Analysis Results
                </h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(neuronInfo).map(([key, value]) => (
                  <div key={key} className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 hover-lift transition-all duration-200">
                    <h4 className="font-medium text-slate-900 dark:text-white mb-2 capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </h4>
                    <p className="text-slate-600 dark:text-slate-300">
                      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Navigation Menu */}
          <div className="mt-12">
            <NavigationMenu className="bg-white dark:bg-slate-800 rounded-xl shadow-lg hover-lift">
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger className="text-slate-900 dark:text-white">
                    Data Sources
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="p-4 w-64">
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Access different neural datasets and analysis tools.
                      </p>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-slate-600 dark:text-slate-400">
            <p>&copy; 2024 Flywire Research Platform. Built for neural network analysis.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
