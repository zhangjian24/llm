import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { RoleProvider } from '../contexts/RoleContext';
import { ChatProvider } from '../contexts/ChatContext';
import { UIProvider } from '../contexts/UIContext';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <RoleProvider>
      <ChatProvider>
        <UIProvider>
          <Component {...pageProps} />
        </UIProvider>
      </ChatProvider>
    </RoleProvider>
  );
}

export default MyApp;
