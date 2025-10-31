<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Client extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'document',
        'contact',
    ];

    protected $casts = [
        'contact' => 'array',
    ];

    public function projects()
    {
        return $this->hasMany(Project::class);
    }
}
