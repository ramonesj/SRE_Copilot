import { create } from 'zustand'

export interface BrandingState {
  companyName: string
  companyLogo: string
  department: string
  contactEmail: string
  setBranding: (data: Partial<Omit<BrandingState, 'setBranding' | 'resetBranding'>>) => void
  resetBranding: () => void
}

const DEFAULT_BRANDING = {
  companyName: 'SRE Copilot',
  companyLogo: '',
  department: 'Autonomous Cloud Reliability Engineering',
  contactEmail: 'sre-oncall@enterprise.com',
}

const STORAGE_KEY = 'sre_copilot_branding'

export const useBrandingStore = create<BrandingState>((set) => {
  const saved = localStorage.getItem(STORAGE_KEY)
  const initial = saved ? { ...DEFAULT_BRANDING, ...JSON.parse(saved) } : DEFAULT_BRANDING

  return {
    ...initial,
    setBranding: (updates) =>
      set((state) => {
        const next = { ...state, ...updates }
        const { companyName, companyLogo, department, contactEmail } = next
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ companyName, companyLogo, department, contactEmail }))
        return next
      }),
    resetBranding: () => {
      localStorage.removeItem(STORAGE_KEY)
      set(DEFAULT_BRANDING)
    },
  }
})
