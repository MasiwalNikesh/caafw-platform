import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  href?: string;
}

export function Card({ children, className, href }: CardProps) {
  const Wrapper = href ? 'a' : 'div';

  return (
    <Wrapper
      href={href}
      className={cn(
        'block rounded-lg border border-gray-200 bg-white p-6',
        'hover:border-indigo-500 hover:shadow-md transition-all duration-200',
        href && 'cursor-pointer',
        className
      )}
    >
      {children}
    </Wrapper>
  );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-start justify-between gap-4', className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <h3 className={cn('text-lg font-semibold text-gray-900 line-clamp-2', className)}>
      {children}
    </h3>
  );
}

export function CardDescription({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={cn('mt-2 text-sm text-gray-600 line-clamp-3', className)}>
      {children}
    </p>
  );
}

export function CardFooter({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('mt-4 flex items-center justify-between', className)}>
      {children}
    </div>
  );
}
