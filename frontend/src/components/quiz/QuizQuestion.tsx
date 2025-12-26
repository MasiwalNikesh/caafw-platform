'use client';

import { useState } from 'react';
import { QuizQuestion as QuizQuestionType } from '@/types';
import { CheckCircle2 } from 'lucide-react';

interface QuizQuestionProps {
  question: QuizQuestionType;
  currentAnswer: string;
  onAnswer: (answer: string) => void;
}

export function QuizQuestion({ question, currentAnswer, onAnswer }: QuizQuestionProps) {
  const [recentlySelected, setRecentlySelected] = useState<string | null>(null);

  const handleSelect = (value: string) => {
    setRecentlySelected(value);
    onAnswer(value);
    setTimeout(() => setRecentlySelected(null), 300);
  };

  const renderMultipleChoice = () => (
    <div className="space-y-3">
      {question.options?.map((option, index) => {
        const isSelected = currentAnswer === option.id;
        const isRecentlySelected = recentlySelected === option.id;
        const letter = String.fromCharCode(65 + index); // A, B, C, D

        return (
          <button
            key={option.id}
            onClick={() => handleSelect(option.id)}
            className={`
              w-full text-left p-4 rounded-xl border-2 transition-all duration-200 group
              ${isSelected
                ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/30 shadow-md shadow-violet-500/10'
                : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 hover:border-violet-300 dark:hover:border-violet-700 hover:bg-violet-50/50 dark:hover:bg-violet-900/20'
              }
              ${isRecentlySelected ? 'scale-[0.98]' : 'scale-100'}
              transform
            `}
          >
            <div className="flex items-center gap-4">
              {/* Letter indicator */}
              <div
                className={`
                  flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center font-semibold text-sm
                  transition-all duration-200
                  ${isSelected
                    ? 'bg-violet-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 group-hover:bg-violet-100 dark:group-hover:bg-violet-900/50 group-hover:text-violet-600 dark:group-hover:text-violet-400'
                  }
                `}
              >
                {isSelected ? <CheckCircle2 className="h-5 w-5" /> : letter}
              </div>
              <span className={`font-medium ${isSelected ? 'text-violet-900 dark:text-violet-100' : 'text-gray-700 dark:text-gray-300'}`}>
                {option.text}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );

  const renderSelfAssessment = () => {
    const scaleLabels = question.scale_labels || {
      '1': 'Strongly Disagree',
      '2': 'Disagree',
      '3': 'Neutral',
      '4': 'Agree',
      '5': 'Strongly Agree',
    };

    return (
      <div className="space-y-6">
        {/* Scale endpoints */}
        <div className="flex justify-between text-sm font-medium px-2">
          <span className="text-gray-500 dark:text-gray-400">{scaleLabels['1']}</span>
          <span className="text-gray-500 dark:text-gray-400">{scaleLabels['5']}</span>
        </div>

        {/* Scale buttons */}
        <div className="flex justify-between gap-2 sm:gap-3">
          {[1, 2, 3, 4, 5].map((value) => {
            const isSelected = currentAnswer === value.toString();
            const isRecentlySelected = recentlySelected === value.toString();

            return (
              <button
                key={value}
                onClick={() => handleSelect(value.toString())}
                className={`
                  flex-1 py-4 sm:py-5 rounded-xl border-2 transition-all duration-200 text-lg font-bold relative overflow-hidden
                  ${isSelected
                    ? 'border-violet-500 bg-gradient-to-br from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30'
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:border-violet-300 dark:hover:border-violet-700 hover:bg-violet-50 dark:hover:bg-violet-900/20 hover:text-violet-600 dark:hover:text-violet-400'
                  }
                  ${isRecentlySelected ? 'scale-95' : 'scale-100 hover:scale-105'}
                  transform
                `}
              >
                {value}
                {isSelected && (
                  <div className="absolute inset-0 bg-white/20 animate-pulse" />
                )}
              </button>
            );
          })}
        </div>

        {/* Full scale labels - desktop only */}
        <div className="hidden sm:flex justify-between text-xs text-gray-400 dark:text-gray-500 px-1">
          {[1, 2, 3, 4, 5].map((value) => (
            <span
              key={value}
              className={`flex-1 text-center transition-colors ${
                currentAnswer === value.toString() ? 'text-violet-600 dark:text-violet-400 font-medium' : ''
              }`}
            >
              {scaleLabels[value.toString()]}
            </span>
          ))}
        </div>

        {/* Selected label - mobile */}
        {currentAnswer && (
          <div className="sm:hidden text-center">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 rounded-full text-sm font-medium">
              <CheckCircle2 className="h-4 w-4" />
              {scaleLabels[currentAnswer]}
            </span>
          </div>
        )}
      </div>
    );
  };

  const renderMultiSelect = () => {
    const selectedAnswers = currentAnswer ? currentAnswer.split(',') : [];

    const toggleOption = (optionId: string) => {
      let newAnswers: string[];
      if (selectedAnswers.includes(optionId)) {
        newAnswers = selectedAnswers.filter((id) => id !== optionId);
      } else {
        newAnswers = [...selectedAnswers, optionId];
      }
      setRecentlySelected(optionId);
      onAnswer(newAnswers.join(','));
      setTimeout(() => setRecentlySelected(null), 300);
    };

    return (
      <div className="space-y-4">
        <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-5 h-5 rounded bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 text-xs font-medium">
            {selectedAnswers.length}
          </span>
          Select all that apply
        </p>
        <div className="space-y-3">
          {question.options?.map((option) => {
            const isSelected = selectedAnswers.includes(option.id);
            const isRecentlySelected = recentlySelected === option.id;

            return (
              <button
                key={option.id}
                onClick={() => toggleOption(option.id)}
                className={`
                  w-full text-left p-4 rounded-xl border-2 transition-all duration-200 group
                  ${isSelected
                    ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/30 shadow-md shadow-violet-500/10'
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 hover:border-violet-300 dark:hover:border-violet-700 hover:bg-violet-50/50 dark:hover:bg-violet-900/20'
                  }
                  ${isRecentlySelected ? 'scale-[0.98]' : 'scale-100'}
                  transform
                `}
              >
                <div className="flex items-center gap-4">
                  {/* Checkbox */}
                  <div
                    className={`
                      w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all duration-200
                      ${isSelected
                        ? 'border-violet-500 bg-violet-500'
                        : 'border-gray-300 dark:border-gray-600 group-hover:border-violet-400 dark:group-hover:border-violet-600'
                      }
                    `}
                  >
                    {isSelected && (
                      <svg
                        className="w-4 h-4 text-white animate-scale-in"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                  <span className={`font-medium ${isSelected ? 'text-violet-900 dark:text-violet-100' : 'text-gray-700 dark:text-gray-300'}`}>
                    {option.text}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Question text */}
      <div className="space-y-2">
        <h3 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white leading-relaxed">
          {question.question_text}
        </h3>
        {question.category && (
          <span className="inline-block text-xs font-medium text-violet-600 dark:text-violet-400 bg-violet-100 dark:bg-violet-900/30 px-2 py-1 rounded-md">
            {question.category}
          </span>
        )}
      </div>

      {/* Answer options */}
      <div>
        {question.question_type === 'multiple_choice' && renderMultipleChoice()}
        {question.question_type === 'self_assessment' && renderSelfAssessment()}
        {question.question_type === 'multi_select' && renderMultiSelect()}
      </div>

      {/* Custom animation styles */}
      <style jsx global>{`
        @keyframes scale-in {
          0% {
            transform: scale(0);
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
          }
        }
        .animate-scale-in {
          animation: scale-in 0.2s ease-out;
        }
      `}</style>
    </div>
  );
}
