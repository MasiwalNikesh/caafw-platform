'use client';

import { QuizQuestion as QuizQuestionType } from '@/types';

interface QuizQuestionProps {
  question: QuizQuestionType;
  currentAnswer: string;
  onAnswer: (answer: string) => void;
}

export function QuizQuestion({ question, currentAnswer, onAnswer }: QuizQuestionProps) {
  const renderMultipleChoice = () => (
    <div className="space-y-3">
      {question.options?.map((option) => (
        <button
          key={option.id}
          onClick={() => onAnswer(option.id)}
          className={`w-full text-left p-4 rounded-lg border transition-all ${
            currentAnswer === option.id
              ? 'border-purple-500 bg-purple-500/20 text-white'
              : 'border-gray-700 bg-gray-800 text-gray-300 hover:border-gray-600 hover:bg-gray-750'
          }`}
        >
          <span className="font-medium">{option.text}</span>
        </button>
      ))}
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
      <div className="space-y-4">
        <div className="flex justify-between text-sm text-gray-400">
          <span>{scaleLabels['1']}</span>
          <span>{scaleLabels['5']}</span>
        </div>
        <div className="flex justify-between gap-2">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              onClick={() => onAnswer(value.toString())}
              className={`flex-1 py-4 rounded-lg border transition-all text-lg font-semibold ${
                currentAnswer === value.toString()
                  ? 'border-purple-500 bg-purple-500/20 text-white'
                  : 'border-gray-700 bg-gray-800 text-gray-300 hover:border-gray-600 hover:bg-gray-750'
              }`}
            >
              {value}
            </button>
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-500 px-2">
          {[1, 2, 3, 4, 5].map((value) => (
            <span key={value} className="flex-1 text-center">
              {scaleLabels[value.toString()]}
            </span>
          ))}
        </div>
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
      onAnswer(newAnswers.join(','));
    };

    return (
      <div className="space-y-3">
        <p className="text-sm text-gray-400 mb-4">Select all that apply</p>
        {question.options?.map((option) => (
          <button
            key={option.id}
            onClick={() => toggleOption(option.id)}
            className={`w-full text-left p-4 rounded-lg border transition-all ${
              selectedAnswers.includes(option.id)
                ? 'border-purple-500 bg-purple-500/20 text-white'
                : 'border-gray-700 bg-gray-800 text-gray-300 hover:border-gray-600 hover:bg-gray-750'
            }`}
          >
            <div className="flex items-center">
              <div
                className={`w-5 h-5 rounded border mr-3 flex items-center justify-center ${
                  selectedAnswers.includes(option.id)
                    ? 'border-purple-500 bg-purple-500'
                    : 'border-gray-600'
                }`}
              >
                {selectedAnswers.includes(option.id) && (
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
              <span className="font-medium">{option.text}</span>
            </div>
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-white">{question.question_text}</h3>
      {question.question_type === 'multiple_choice' && renderMultipleChoice()}
      {question.question_type === 'self_assessment' && renderSelfAssessment()}
      {question.question_type === 'multi_select' && renderMultiSelect()}
    </div>
  );
}
