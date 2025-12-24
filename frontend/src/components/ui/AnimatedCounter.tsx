'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useInView, useSpring, useTransform } from 'framer-motion';

interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
  className?: string;
}

export function AnimatedCounter({
  value,
  suffix = '',
  prefix = '',
  duration = 2,
  className = '',
}: AnimatedCounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [hasAnimated, setHasAnimated] = useState(false);

  const spring = useSpring(0, {
    stiffness: 50,
    damping: 30,
    duration: duration * 1000,
  });

  const display = useTransform(spring, (current) => {
    return Math.floor(current);
  });

  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (isInView && !hasAnimated) {
      spring.set(value);
      setHasAnimated(true);
    }
  }, [isInView, value, spring, hasAnimated]);

  useEffect(() => {
    return display.on('change', (latest) => {
      setDisplayValue(latest);
    });
  }, [display]);

  return (
    <span ref={ref} className={className}>
      {prefix}
      {displayValue}
      {suffix}
    </span>
  );
}

// Simple animated number display (e.g., "100+")
interface AnimatedStatProps {
  value: string;
  label: string;
  delay?: number;
  className?: string;
}

export function AnimatedStat({ value, label, delay = 0, className = '' }: AnimatedStatProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.25, 0.1, 0.25, 1],
      }}
      className={className}
    >
      <motion.p
        initial={{ scale: 0.5 }}
        animate={isInView ? { scale: 1 } : { scale: 0.5 }}
        transition={{
          duration: 0.5,
          delay: delay + 0.1,
          ease: [0.25, 0.1, 0.25, 1],
        }}
        className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 bg-clip-text text-transparent"
      >
        {value}
      </motion.p>
      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{label}</p>
    </motion.div>
  );
}

