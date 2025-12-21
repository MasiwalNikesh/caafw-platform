'use client';

import { OAuthCallbackHandler } from '@/components/auth/OAuthCallbackHandler';

export default function LinkedInCallbackPage() {
  return <OAuthCallbackHandler provider="linkedin" />;
}
